from __future__ import annotations

import collections.abc
import io
import itertools
import time
import typing

from marrow.compiler.backend.macroop import MacroOpVisitor

from .constants import REGISTER_COUNT
from .constants import REGISTER_INDEXES
from .constants import REGISTER_SIZE
from .rat import ReadAccess
from .rat import WriteAccess

if typing.TYPE_CHECKING:
    from marrow.compiler.backend.macroop import Add
    from marrow.compiler.backend.macroop import Div
    from marrow.compiler.backend.macroop import DumpMemory
    from marrow.compiler.backend.macroop import Load
    from marrow.compiler.backend.macroop import MacroOp
    from marrow.compiler.backend.macroop import Mod
    from marrow.compiler.backend.macroop import Mul
    from marrow.compiler.backend.macroop import Neg
    from marrow.compiler.backend.macroop import Pos
    from marrow.compiler.backend.macroop import Store
    from marrow.compiler.backend.macroop import StoreImmediate
    from marrow.compiler.backend.macroop import Sub
    from marrow.logger import Logger
    from marrow.types import MemoryAddress
    from marrow.types import RegisterNumber

    from .rat import Access


class Machine(MacroOpVisitor[None]):
    MEMORY_SIZE = 0x10000
    SECTION_SIZE = 0x100

    def __init__(self, logger: Logger) -> None:
        self.register_file = bytearray(REGISTER_SIZE * REGISTER_COUNT)
        self.bank_mapping: dict[RegisterNumber, int] = {
            index: index * REGISTER_SIZE for index in REGISTER_INDEXES
        }

        self.memory = bytearray(Machine.MEMORY_SIZE)

        self.old_registers: list[int | float] = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]
        self.old_memory: list[int | float] = [0 for _ in range(self.MEMORY_SIZE)]

        self.register_tracking: set[RegisterNumber] = set()
        self.access_tracking: list[Access] = []

        self.logger = logger

    def get_register_raw(self, number: RegisterNumber) -> bytearray:
        self.access_tracking.append(ReadAccess(number))
        index = self.bank_mapping[number]

        return self.register_file[index : index + REGISTER_SIZE]

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
        size: int,
        payload: bytearray,
    ) -> None:
        if size <= 0:
            return

        payload_size = len(payload)

        self.memory[address : address + size] = payload[
            payload_size - size : payload_size
        ]

    def visit_load(self, op: Load) -> None:
        self.old_registers[op.destination] = self.old_memory[op.source]

        self.set_register_raw(
            op.destination,
            self.get_memory_raw(op.source, REGISTER_SIZE),
        )

    def visit_store(self, op: Store) -> None:
        self.old_memory[op.destination] = self.old_registers[op.source]

        self.set_memory_raw(
            op.destination,
            REGISTER_SIZE,
            self.get_register_raw(op.source),
        )

    def visit_store_immediate(self, op: StoreImmediate) -> None:
        self.old_memory[op.destination] = op.immediate

        # NOTE: to use the new memory API, immediate values must be sized

    def visit_add(self, op: Add) -> None:
        self.old_registers[op.destination] = (
            self.old_registers[op.left] + self.old_registers[op.right]
        )

    def visit_sub(self, op: Sub) -> None:
        self.old_registers[op.destination] = (
            self.old_registers[op.left] - self.old_registers[op.right]
        )

    def visit_mul(self, op: Mul) -> None:
        self.old_registers[op.destination] = (
            self.old_registers[op.left] * self.old_registers[op.right]
        )

    def visit_div(self, op: Div) -> None:
        left = self.old_registers[op.left]
        right = self.old_registers[op.right]

        self.old_registers[op.destination] = (
            left // right
            if isinstance(left, int) and isinstance(right, int)
            else left / right
        )

    def visit_mod(self, op: Mod) -> None:
        self.old_registers[op.destination] = (
            self.old_registers[op.left] % self.old_registers[op.right]
        )

    def visit_pos(self, op: Pos) -> None:
        self.old_registers[op.destination] = +self.old_registers[op.source]

    def visit_neg(self, op: Neg) -> None:
        self.old_registers[op.destination] = -self.old_registers[op.source]

    def visit_dump_memory(self, op: DumpMemory) -> None:
        self.logger.debug(self._generate_dump_old_memory_log(op.section_id))
        self.logger.debug(self._generate_dump_memory_log(op.section_id))

    def _to_hex_representation(self, value: int | float) -> str:
        base_repr = f"{int(value):02x}"

        if value == 0:
            return f"\x1b[2m{base_repr}\x1b[22m"

        return base_repr

    def _generate_dump_old_memory_log(self, section_id: int) -> str:
        buffer = io.StringIO()
        start = section_id * self.SECTION_SIZE
        section = self.old_memory[start : start + self.SECTION_SIZE]

        print(f"<deprecated> memory dump (section {section_id:#x})", file=buffer)

        for row in itertools.batched(section, 16):
            print(*map(self._to_hex_representation, row), file=buffer)

        return buffer.getvalue()

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
            self.logger.debug(f"execution time: {time_end - time_start:.4f}s")
            self.logger.debug(
                f"registers used: {', '.join(map(hex, self.register_tracking))}",
            )
            self.logger.debug(self._generate_register_access_log())
