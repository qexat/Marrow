# pyright: reportImportCycles = false

from __future__ import annotations

import enum
import typing

from marrow.runtime.alu.op import ALUOpVisitor

if typing.TYPE_CHECKING:
    from marrow.runtime.alu.op import Add
    from marrow.runtime.alu.op import ALUOp
    from marrow.runtime.alu.op import Div
    from marrow.runtime.alu.op import Mod
    from marrow.runtime.alu.op import Mul
    from marrow.runtime.alu.op import Sub
    from marrow.tooling import GlobalTooling


class UnitFlags(enum.IntFlag):
    OVERFLOW = enum.auto()
    NEGATIVE = enum.auto()
    DIV_BY_ZERO = enum.auto()


class ArithmeticLogicUnit(ALUOpVisitor[bytearray]):
    def __init__(self, tooling: GlobalTooling) -> None:
        self.flags = UnitFlags(0)

        self.tooling = tooling

    def reset_flags(self) -> None:
        self.flags = UnitFlags(0)

    def visit_add(self, op: Add) -> bytearray:
        self.reset_flags()

        left = self.tooling.endec.decode_integer(op.left)
        right = self.tooling.endec.decode_integer(op.right)

        result = left + right

        if self.tooling.endec.does_integer_overflow(result):
            self.flags |= UnitFlags.OVERFLOW

        return self.tooling.endec.encode_integer(result)

    def visit_div(self, op: Div) -> bytearray:
        self.reset_flags()

        left = self.tooling.endec.decode_integer(op.left)
        right = self.tooling.endec.decode_integer(op.right)

        if right == 0:
            self.flags |= UnitFlags.DIV_BY_ZERO

            return bytearray(8)

        return self.tooling.endec.encode_integer(left // right)

    def visit_mod(self, op: Mod) -> bytearray:
        self.reset_flags()

        left = self.tooling.endec.decode_integer(op.left)
        right = self.tooling.endec.decode_integer(op.right)

        if right == 0:
            self.flags |= UnitFlags.DIV_BY_ZERO

            return bytearray(8)

        return self.tooling.endec.encode_integer(left % right)

    def visit_mul(self, op: Mul) -> bytearray:
        self.reset_flags()

        left = self.tooling.endec.decode_integer(op.left)
        right = self.tooling.endec.decode_integer(op.right)

        result = left * right

        if self.tooling.endec.does_integer_overflow(result):
            self.flags |= UnitFlags.OVERFLOW

        return self.tooling.endec.encode_integer(result)

    def visit_sub(self, op: Sub) -> bytearray:
        self.reset_flags()

        left = self.tooling.endec.decode_integer(op.left)
        right = self.tooling.endec.decode_integer(op.right)

        return self.tooling.endec.encode_integer(left - right)

    def execute(self, op: ALUOp) -> bytearray:
        return op.accept(self)
