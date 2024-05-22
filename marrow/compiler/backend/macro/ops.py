from __future__ import annotations

import abc
import enum
import typing

import attrs

if typing.TYPE_CHECKING:
    from marrow.types import ImmediateType
    from marrow.types import MemoryAddress
    from marrow.types import RegisterNumber


class ArithmeticFunc(enum.IntEnum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MOD = enum.auto()


class MacroOpVisitor[R_co](typing.Protocol):
    def visit_load(self, op: Load) -> R_co: ...
    def visit_store(self, op: Store) -> R_co: ...
    def visit_store_immediate(self, op: StoreImmediate) -> R_co: ...

    def visit_add(self, op: Add) -> R_co: ...
    def visit_sub(self, op: Sub) -> R_co: ...
    def visit_mul(self, op: Mul) -> R_co: ...
    def visit_div(self, op: Div) -> R_co: ...
    def visit_mod(self, op: Mod) -> R_co: ...

    def visit_pos(self, op: Pos) -> R_co: ...
    def visit_neg(self, op: Neg) -> R_co: ...

    def visit_dump_memory(self, op: DumpMemory) -> R_co: ...


class MacroOpBase(abc.ABC):
    @abc.abstractmethod
    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        pass


@attrs.frozen
class Load(MacroOpBase):
    destination: RegisterNumber
    source: MemoryAddress

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_load(self)


@attrs.frozen
class Store(MacroOpBase):
    destination: MemoryAddress
    source: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_store(self)


@attrs.frozen
class StoreImmediate(MacroOpBase):
    destination: MemoryAddress
    type: ImmediateType
    immediate: bytearray

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_store_immediate(self)


@attrs.frozen
class Add(MacroOpBase):
    destination: RegisterNumber
    type: ImmediateType
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_add(self)


@attrs.frozen
class Sub(MacroOpBase):
    destination: RegisterNumber
    type: ImmediateType
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_sub(self)


@attrs.frozen
class Mul(MacroOpBase):
    destination: RegisterNumber
    type: ImmediateType
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_mul(self)


@attrs.frozen
class Div(MacroOpBase):
    destination: RegisterNumber
    type: ImmediateType
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_div(self)


@attrs.frozen
class Mod(MacroOpBase):
    destination: RegisterNumber
    type: ImmediateType
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_mod(self)


@attrs.frozen
class Pos(MacroOpBase):
    destination: RegisterNumber
    type: ImmediateType
    source: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_pos(self)


@attrs.frozen
class Neg(MacroOpBase):
    destination: RegisterNumber
    type: ImmediateType
    source: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_neg(self)


@attrs.frozen
class DumpMemory(MacroOpBase):
    section_id: int

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_dump_memory(self)


type LoadStoreMacroOp = Load | Store | StoreImmediate
type BinOpMacroOp = Add | Sub | Mul | Div | Mod
type UnOpMacroOp = Pos | Neg
type DebugMacroOp = DumpMemory
type MacroOp = LoadStoreMacroOp | BinOpMacroOp | UnOpMacroOp | DebugMacroOp
