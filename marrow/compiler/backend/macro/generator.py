from __future__ import annotations

import collections.abc
import io
import typing

from marrow.compiler.backend.funcs import BinaryArithFunc
from marrow.compiler.backend.funcs import UnaryArithFunc
from marrow.compiler.common import TokenType
from marrow.compiler.middleend.SSAIR.rvalue import AtomRValue
from marrow.compiler.middleend.SSAIR.rvalue import BinaryRValue
from marrow.compiler.middleend.SSAIR.rvalue import UnaryRValue
from marrow.types import ImmediateType

from .ops import BinaryArith
from .ops import Load
from .ops import Store
from .ops import StoreImmediate
from .ops import UnaryArith

if typing.TYPE_CHECKING:
    from marrow.compiler.common import BinaryOpTokenType
    from marrow.compiler.common import IRInstruction
    from marrow.compiler.common import LiteralTokenType
    from marrow.compiler.common import Token
    from marrow.compiler.common import UnaryOpTokenType
    from marrow.endec import EnDec
    from marrow.logger import Logger
    from marrow.types import MemoryAddress
    from marrow.types import RegisterNumber

    from .ops import MacroOp


BINOP_FUNC_MAPPING: dict[BinaryOpTokenType, BinaryArithFunc] = {
    TokenType.MINUS: BinaryArithFunc.SUB,
    TokenType.PERCENT: BinaryArithFunc.MOD,
    TokenType.PLUS: BinaryArithFunc.ADD,
    TokenType.SLASH: BinaryArithFunc.DIV,
    TokenType.STAR: BinaryArithFunc.MUL,
}

UNOP_FUNC_MAPPING: dict[UnaryOpTokenType, UnaryArithFunc] = {
    TokenType.MINUS: UnaryArithFunc.NEG,
    TokenType.PLUS: UnaryArithFunc.POS,
}


class MacroOpGenerator:
    def __init__(self, logger: Logger, encoder_decoder: EnDec) -> None:
        self.ops: list[MacroOp] = []
        self.available_registers: list[RegisterNumber] = [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
        ]
        # `available_registers` is a stack with the top being the end.
        # since we allocate the lowest registers first, we have the put them
        # at the end
        self.available_registers.reverse()

        self.logger = logger
        self.encoder_decoder = encoder_decoder

    def allocate_register(self) -> RegisterNumber:
        if not self.available_registers:
            raise RuntimeError("critical error: no available registers")

        index = self.available_registers.pop()

        return index

    def free_register(self, index: RegisterNumber) -> None:
        if index in self.available_registers:
            raise ValueError(f"cannot free register {index!r}: already freed")

        self.available_registers.append(index)

    def free_registers(self, *indexes: RegisterNumber) -> None:
        for index in indexes:
            self.free_register(index)

    def add_ops(self, *ops: MacroOp) -> None:
        self.ops.extend(ops)

    def lower_atom_op(self, destination: MemoryAddress, token: Token) -> None:
        match typing.cast("LiteralTokenType", token.type):
            case TokenType.INTEGER:
                # TODO: check if int fits in 64 bits
                value = int(token.lexeme)
                type = ImmediateType.INTEGER
            case TokenType.FLOAT:
                # TODO: check if float fits in 64 bits
                value = float(token.lexeme)
                type = ImmediateType.FLOAT

        immediate = self.encoder_decoder.encode_immediate(value)

        op = StoreImmediate(destination, type, immediate)
        self.add_ops(op)

    def lower_binary_op(
        self,
        kind: BinaryOpTokenType,
        destination: MemoryAddress,
        left: MemoryAddress,
        right: MemoryAddress,
    ) -> None:
        rdestination = self.allocate_register()
        rleft = self.allocate_register()
        rright = self.allocate_register()

        func = BINOP_FUNC_MAPPING[kind]

        self.add_ops(
            Load(rleft, left),
            Load(rright, right),
            # NOTE: in the future, the SSA IR will be produced from a typed AST
            # so we won't have to hardcode the binop type, we will just grab
            # the data from the SSA IR instruction
            BinaryArith(func, ImmediateType.INTEGER, rdestination, rleft, rright),
            Store(destination, rdestination),
        )

        self.free_registers(rdestination, rleft, rright)

    def lower_unary_op(
        self,
        kind: UnaryOpTokenType,
        destination: MemoryAddress,
        right: MemoryAddress,
    ) -> None:
        rdestination = self.allocate_register()
        rright = self.allocate_register()

        func = UNOP_FUNC_MAPPING[kind]

        self.add_ops(
            Load(rright, right),
            # NOTE: in the future, the SSA IR will be produced from a typed AST
            # so we won't have to hardcode the binop type, we will just grab
            # the data from the SSA IR instruction
            UnaryArith(func, ImmediateType.INTEGER, rdestination, rright),
            Store(destination, rdestination),
        )

        self.free_registers(rdestination, rright)

    def lower(self, instruction: IRInstruction) -> None:
        match instruction.rvalue:
            case AtomRValue(token):
                self.lower_atom_op(instruction.destination, token)
            case BinaryRValue(kind, left, right):
                self.lower_binary_op(kind, instruction.destination, left, right)
            case UnaryRValue(kind, right):
                self.lower_unary_op(kind, instruction.destination, right)

    def generate_log_nonfreed_registers(self, non_freed_registers: list[int]) -> str:
        buffer = io.StringIO()

        print(
            f"macro op generation has finished, but {len(non_freed_registers)} register(s) are still allocated",
            file=buffer,
        )

        for index in non_freed_registers:
            print(f"register {index:#x} was never freed", file=buffer)

        return buffer.getvalue()

    def generate(
        self,
        ir: collections.abc.Iterable[IRInstruction],
    ) -> list[MacroOp]:
        for instruction in ir:
            self.lower(instruction)

        nonfreed_registers = [
            index for index in range(1, 16) if index not in self.available_registers
        ]

        if nonfreed_registers:
            self.logger.warn(self.generate_log_nonfreed_registers(nonfreed_registers))

        return self.ops
