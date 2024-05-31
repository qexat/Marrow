from __future__ import annotations

import abc
import typing

import attrs

if typing.TYPE_CHECKING:
    from marrow.types import ImmediateType
    from marrow.types import MemoryAddress
    from marrow.types import RegisterNumber

    from ..funcs import BinaryArithmeticFunc
    from ..funcs import UnaryArithmeticFunc


class MacroOpVisitor[R_co](typing.Protocol):
    def visit_load(self, op: Load) -> R_co: ...
    def visit_store(self, op: Store) -> R_co: ...
    def visit_store_immediate(self, op: StoreImmediate) -> R_co: ...
    def visit_push(self, op: Push) -> R_co: ...
    def visit_pop(self, op: Pop) -> R_co: ...

    def visit_binary_arithmetic(self, op: BinaryArithmetic) -> R_co: ...
    def visit_unary_arithmetic(self, op: UnaryArithmetic) -> R_co: ...

    def visit_dump_memory(self, op: DumpHeap) -> R_co: ...


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
class Push(MacroOpBase):
    type: ImmediateType
    source: bytearray

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_push(self)


@attrs.frozen
class Pop(MacroOpBase):
    type: ImmediateType
    destination: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_pop(self)


@attrs.frozen
class BinaryArithmetic(MacroOpBase):
    func: BinaryArithmeticFunc
    type: ImmediateType
    destination: RegisterNumber
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_binary_arithmetic(self)


@attrs.frozen
class UnaryArithmetic(MacroOpBase):
    func: UnaryArithmeticFunc
    type: ImmediateType
    destination: RegisterNumber
    source: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_unary_arithmetic(self)


# !! TEMPORARY !! #
@attrs.frozen
class DumpHeap(MacroOpBase):
    section_id: int

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_dump_memory(self)


type LoadStoreMacroOp = Load | Store | StoreImmediate
type StackMacroOp = Push | Pop
type DebugMacroOp = DumpHeap
type MacroOp = LoadStoreMacroOp | BinaryArithmetic | UnaryArithmetic | DebugMacroOp
