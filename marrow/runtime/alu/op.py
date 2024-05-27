from __future__ import annotations

import abc
import collections.abc
import functools
import typing

import attrs

from marrow.compiler.backend.funcs import BinaryArithmeticFunc
from marrow.compiler.backend.funcs import UnaryArithmeticFunc


class ALUOpVisitor[R_co](typing.Protocol):
    def visit_add(self, op: Add) -> R_co: ...
    def visit_div(self, op: Div) -> R_co: ...
    def visit_mod(self, op: Mod) -> R_co: ...
    def visit_mul(self, op: Mul) -> R_co: ...
    def visit_sub(self, op: Sub) -> R_co: ...


class ALUOpBase(abc.ABC):
    @abc.abstractmethod
    def accept[R](self, visitor: ALUOpVisitor[R]) -> R:
        pass


@attrs.frozen
class Add(ALUOpBase):
    left: bytearray
    right: bytearray

    def accept[R](self, visitor: ALUOpVisitor[R]) -> R:
        return visitor.visit_add(self)


@attrs.frozen
class Div(ALUOpBase):
    left: bytearray
    right: bytearray

    def accept[R](self, visitor: ALUOpVisitor[R]) -> R:
        return visitor.visit_div(self)


@attrs.frozen
class Mod(ALUOpBase):
    left: bytearray
    right: bytearray

    def accept[R](self, visitor: ALUOpVisitor[R]) -> R:
        return visitor.visit_mod(self)


@attrs.frozen
class Mul(ALUOpBase):
    left: bytearray
    right: bytearray

    def accept[R](self, visitor: ALUOpVisitor[R]) -> R:
        return visitor.visit_mul(self)


@attrs.frozen
class Sub(ALUOpBase):
    left: bytearray
    right: bytearray

    def accept[R](self, visitor: ALUOpVisitor[R]) -> R:
        return visitor.visit_sub(self)


type ALUOp = Add | Div | Mod | Mul | Sub

BINOP_MAPPING: dict[BinaryArithmeticFunc, type[ALUOp]] = {
    BinaryArithmeticFunc.ADD: Add,
    BinaryArithmeticFunc.DIV: Div,
    BinaryArithmeticFunc.MOD: Mod,
    BinaryArithmeticFunc.MUL: Mul,
    BinaryArithmeticFunc.SUB: Sub,
}

type _PartialOp = collections.abc.Callable[[bytearray], ALUOp]

UNOP_MAPPING: dict[UnaryArithmeticFunc, _PartialOp] = {
    UnaryArithmeticFunc.NEG: functools.partial(Sub, 0),
    UnaryArithmeticFunc.POS: functools.partial(Add, 0),
}
