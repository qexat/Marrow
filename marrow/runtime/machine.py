from __future__ import annotations

import collections.abc
import io
import itertools
import time
import typing

from marrow.compiler.backend.macro.ops import MacroOpVisitor
from marrow.compiler.backend.macro.ops import UnaryArithmetic
from marrow.runtime.alu.alu import UnitFlags
from marrow.tooling import RuntimeTooling
from marrow.types import ImmediateType
from marrow.types import RuntimeType

from .alu.op import BINOP_MAPPING
from .alu.op import UNOP_MAPPING
from .constants import REGISTER_COUNT
from .constants import REGISTER_INDEXES
from .constants import REGISTER_SIZE
from .rat import ReadAccess
from .rat import WriteAccess

if typing.TYPE_CHECKING:
    from marrow.compiler.backend.macro.ops import BinaryArithmetic
    from marrow.compiler.backend.macro.ops import DumpMemory
    from marrow.compiler.backend.macro.ops import Load
    from marrow.compiler.backend.macro.ops import Store
    from marrow.compiler.backend.macro.ops import StoreImmediate
    from marrow.compiler.common import MacroOp
    from marrow.tooling import GlobalTooling
    from marrow.types import ByteCount
    from marrow.types import MemoryAddress
    from marrow.types import RegisterNumber

    from .rat import Access


class Machine(MacroOpVisitor[None]):
    MEMORY_SIZE = 0x10000
    SECTION_SIZE = 0x100

    def __init__(self, tooling: GlobalTooling) -> None:
        self.register_file = bytearray(REGISTER_SIZE * REGISTER_COUNT)
        self.bank_mapping: dict[RegisterNumber, int] = {
            index: index * REGISTER_SIZE for index in REGISTER_INDEXES
        }

        self.memory = bytearray(Machine.MEMORY_SIZE)

        self.access_tracking: list[Access] = []
        self.tooling = RuntimeTooling.from_global(tooling)

    @typing.overload
    def get_register(
        self,
        number: RegisterNumber,
        type: typing.Literal[ImmediateType.FLOAT],
    ) -> float: ...
    @typing.overload
    def get_register(
        self,
        number: RegisterNumber,
        type: typing.Literal[ImmediateType.INTEGER],
    ) -> int: ...
    @typing.overload
    def get_register(
        self,
        number: RegisterNumber,
        type: ImmediateType,
    ) -> RuntimeType: ...

    def get_register(self, number: RegisterNumber, type: ImmediateType) -> RuntimeType:
        value = self.get_register_raw(number)

        return self.tooling.endec.decode_immediate(value, type)

    def get_register_raw(self, number: RegisterNumber) -> bytearray:
        self.access_tracking.append(ReadAccess(number))
        index = self.bank_mapping[number]

        return self.register_file[index : index + REGISTER_SIZE]

    def set_register(self, number: RegisterNumber, value: RuntimeType) -> None:
        raw_value = self.tooling.endec.encode_immediate(value)

        self.set_register_raw(number, raw_value)

    def set_register_raw(self, number: RegisterNumber, value: bytearray) -> None:
        self.access_tracking.append(WriteAccess(number, value))
        index = self.bank_mapping[number]

        self.register_file[index : index + REGISTER_SIZE] = value

    # TODO: bound checking
    def get_memory_raw(self, address: MemoryAddress, size: int) -> bytearray:
        if size <= 0:
            return bytearray()

        return self.memory[address : address + size]

    # TODO: bound checking
    def set_memory_raw(
        self,
        address: MemoryAddress,
        size: ByteCount,
        payload: bytearray,
    ) -> None:
        if size <= 0:
            return

        payload_size = len(payload)

        self.memory[address : address + size] = payload[
            payload_size - size : payload_size
        ]

    def visit_load(self, op: Load) -> None:
        self.set_register_raw(
            op.destination,
            self.get_memory_raw(op.source * REGISTER_SIZE, REGISTER_SIZE),
        )

    def visit_store(self, op: Store) -> None:
        self.set_memory_raw(
            op.destination * REGISTER_SIZE,
            REGISTER_SIZE,
            self.get_register_raw(op.source),
        )

    def visit_store_immediate(self, op: StoreImmediate) -> None:
        self.set_memory_raw(op.destination * REGISTER_SIZE, REGISTER_SIZE, op.immediate)

    def visit_binary_arithmetic(self, op: BinaryArithmetic) -> None:
        left = self.get_register_raw(op.left)
        right = self.get_register_raw(op.right)

        result = self.tooling.alu.execute(BINOP_MAPPING[op.func](left, right))

        if UnitFlags.OVERFLOW in self.tooling.alu.flags:
            self.tooling.logger.warn("overflow detected")

        self.set_register_raw(op.destination, result)

    def visit_unary_arithmetic(self, op: UnaryArithmetic) -> None:
        right = self.get_register_raw(op.source)

        result = self.tooling.alu.execute(UNOP_MAPPING[op.func](right))

        self.set_register_raw(op.destination, result)

    def visit_dump_memory(self, op: DumpMemory) -> None:
        self.tooling.logger.debug(self._generate_dump_memory_log(op.section_id))

    def _to_hex_representation(self, value: RuntimeType) -> str:
        # FIXME: add support for more types
        # yucky, but we actually don't have floats anyway (for now)
        base_repr = f"{int(value):02x}"

        if value == 0:
            return f"\x1b[2m{base_repr}\x1b[22m"

        return base_repr

    def _generate_dump_memory_log(self, section_id: int) -> str:
        buffer = io.StringIO()
        start = section_id * Machine.SECTION_SIZE
        section = self.memory[start : start + Machine.SECTION_SIZE]

        print(f"memory dump (section {section_id:#x})", file=buffer)

        for row in itertools.batched(section, 16):
            print(*map(self._to_hex_representation, row), file=buffer)

        return buffer.getvalue()

    def _generate_register_access_log(self) -> str:
        buffer = io.StringIO()

        print("register access log", file=buffer)

        # TODO: use a dedicated structure for traversing
        for access in self.access_tracking:
            match access:
                case ReadAccess(number):
                    print(f"- read from register {number:#x}", file=buffer)
                case WriteAccess(number, _):
                    print(f"- write to register {number:#x}", file=buffer)

        return buffer.getvalue()

    def visit_op(self, op: MacroOp) -> None:
        op.accept(self)

    def execute(
        self,
        ops: collections.abc.Iterable[MacroOp],
        *,
        debug: bool = False,
    ) -> None:
        time_start = time.perf_counter()

        for op in ops:
            self.visit_op(op)

        time_end = time.perf_counter()

        if debug:
            self.tooling.logger.debug(f"execution time: {time_end - time_start:.4f}s")
            self.tooling.logger.debug(self._generate_register_access_log())
