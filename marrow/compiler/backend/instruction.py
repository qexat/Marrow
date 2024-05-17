from __future__ import annotations

import abc
import typing

import attrs

if typing.TYPE_CHECKING:
    from marrow.compiler.types import MemoryLocation
    from marrow.types import RegisterIndex


class InstructionVisitor[R_co](typing.Protocol):
    def visit_load(self, instruction: Load) -> R_co: ...
    def visit_store(self, instruction: Store) -> R_co: ...
    def visit_store_immediate(self, instruction: StoreImmediate) -> R_co: ...

    def visit_add(self, instruction: Add) -> R_co: ...
    def visit_sub(self, instruction: Sub) -> R_co: ...
    def visit_mul(self, instruction: Mul) -> R_co: ...
    def visit_div(self, instruction: Div) -> R_co: ...
    def visit_mod(self, instruction: Mod) -> R_co: ...

    def visit_pos(self, instruction: Pos) -> R_co: ...
    def visit_neg(self, instruction: Neg) -> R_co: ...

    def visit_dump_memory(self, instruction: DumpMemory) -> R_co: ...


class InstructionBase(abc.ABC):
    @abc.abstractmethod
    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        pass


@attrs.frozen
class Load(InstructionBase):
    destination: RegisterIndex
    source: MemoryLocation

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_load(self)


@attrs.frozen
class Store(InstructionBase):
    destination: MemoryLocation
    source: RegisterIndex

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_store(self)


@attrs.frozen
class StoreImmediate(InstructionBase):
    destination: MemoryLocation
    immediate: int | float

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_store_immediate(self)


@attrs.frozen
class Add(InstructionBase):
    destination: RegisterIndex
    left: RegisterIndex
    right: RegisterIndex

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_add(self)


@attrs.frozen
class Sub(InstructionBase):
    destination: RegisterIndex
    left: RegisterIndex
    right: RegisterIndex

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_sub(self)


@attrs.frozen
class Mul(InstructionBase):
    destination: RegisterIndex
    left: RegisterIndex
    right: RegisterIndex

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_mul(self)


@attrs.frozen
class Div(InstructionBase):
    destination: RegisterIndex
    left: RegisterIndex
    right: RegisterIndex

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_div(self)


@attrs.frozen
class Mod(InstructionBase):
    destination: RegisterIndex
    left: RegisterIndex
    right: RegisterIndex

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_mod(self)


@attrs.frozen
class Pos(InstructionBase):
    destination: RegisterIndex
    source: RegisterIndex

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_pos(self)


@attrs.frozen
class Neg(InstructionBase):
    destination: RegisterIndex
    source: RegisterIndex

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_neg(self)


@attrs.frozen
class DumpMemory(InstructionBase):
    section_id: int

    def accept[R](self, visitor: InstructionVisitor[R]) -> R:
        return visitor.visit_dump_memory(self)


type LoadStoreInstruction = Load | Store | StoreImmediate
type BinOpInstruction = Add | Sub | Mul | Div | Mod
type UnOpInstruction = Pos | Neg
type DebugInstruction = DumpMemory
type Instruction = (
    LoadStoreInstruction | BinOpInstruction | UnOpInstruction | DebugInstruction
)
