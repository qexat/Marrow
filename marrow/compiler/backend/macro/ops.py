from __future__ import annotations

import abc
import typing

import attrs

if typing.TYPE_CHECKING:
    from marrow.types import ImmediateType
    from marrow.types import MemoryAddress
    from marrow.types import RegisterNumber

    from ..funcs import BinaryArithFunc
    from ..funcs import UnaryArithFunc


class MacroOpVisitor[R_co](typing.Protocol):
    def visit_load(self, op: Load) -> R_co: ...
    def visit_store(self, op: Store) -> R_co: ...
    def visit_store_immediate(self, op: StoreImmediate) -> R_co: ...

    def visit_binary_arith(self, op: BinaryArith) -> R_co: ...
    def visit_unary_arith(self, op: UnaryArith) -> R_co: ...

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
class BinaryArith(MacroOpBase):
    func: BinaryArithFunc
    type: ImmediateType
    destination: RegisterNumber
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_binary_arith(self)


@attrs.frozen
class UnaryArith(MacroOpBase):
    func: UnaryArithFunc
    type: ImmediateType
    destination: RegisterNumber
    source: RegisterNumber

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_unary_arith(self)


@attrs.frozen
class DumpMemory(MacroOpBase):
    section_id: int

    def accept[R](self, visitor: MacroOpVisitor[R]) -> R:
        return visitor.visit_dump_memory(self)


type LoadStoreMacroOp = Load | Store | StoreImmediate
type DebugMacroOp = DumpMemory
type MacroOp = LoadStoreMacroOp | BinaryArith | UnaryArith | DebugMacroOp
