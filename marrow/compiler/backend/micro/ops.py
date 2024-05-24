from __future__ import annotations

import abc
import typing

import attrs

if typing.TYPE_CHECKING:
    from marrow.types import MemoryAddress
    from marrow.types import RegisterNumber

    from ..funcs import BinaryArithmeticFunc
    from ..funcs import UnaryArithmeticFunc


class MicroOpVisitor[R_co](typing.Protocol):
    def visit_load_address(self, op: LoadAddress) -> R_co: ...
    def visit_load_immediate_8(self, op: LoadImmediate8) -> R_co: ...
    def visit_load_immediate_16(self, op: LoadImmediate16) -> R_co: ...
    def visit_load_immediate_32(self, op: LoadImmediate32) -> R_co: ...
    def visit_load_immediate_64(self, op: LoadImmediate64) -> R_co: ...

    def visit_store_register(self, op: StoreRegister) -> R_co: ...
    def visit_store_immediate_8(self, op: StoreImmediate8) -> R_co: ...
    def visit_store_immediate_16(self, op: StoreImmediate16) -> R_co: ...
    def visit_store_immediate_32(self, op: StoreImmediate32) -> R_co: ...
    def visit_store_immediate_64(self, op: StoreImmediate64) -> R_co: ...

    def visit_binary_arithmetic_int8(self, op: BinaryArithmeticInt8) -> R_co: ...
    def visit_binary_arithmetic_int16(self, op: BinaryArithmeticInt16) -> R_co: ...
    def visit_binary_arithmetic_int32(self, op: BinaryArithmeticInt32) -> R_co: ...
    def visit_binary_arithmetic_int64(self, op: BinaryArithmeticInt64) -> R_co: ...
    def visit_binary_arithmetic_float(self, op: BinaryArithmeticFloat) -> R_co: ...

    def visit_unary_arithmetic_int8(self, op: UnaryArithmeticInt8) -> R_co: ...
    def visit_unary_arithmetic_int16(self, op: UnaryArithmeticInt16) -> R_co: ...
    def visit_unary_arithmetic_int32(self, op: UnaryArithmeticInt32) -> R_co: ...
    def visit_unary_arithmetic_int64(self, op: UnaryArithmeticInt64) -> R_co: ...
    def visit_unary_arithmetic_float(self, op: UnaryArithmeticFloat) -> R_co: ...

    def visit_dump_memory(self, op: DumpMemory) -> R_co: ...


class MicroOpBase(abc.ABC):
    @abc.abstractmethod
    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        pass


@attrs.frozen
class LoadAddress(MicroOpBase):
    destination: RegisterNumber
    source: MemoryAddress

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_load_address(self)


@attrs.frozen
class LoadImmediate8(MicroOpBase):
    destination: RegisterNumber
    immediate: bytearray

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_load_immediate_8(self)


@attrs.frozen
class LoadImmediate16(MicroOpBase):
    destination: RegisterNumber
    immediate: bytearray

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_load_immediate_16(self)


@attrs.frozen
class LoadImmediate32(MicroOpBase):
    destination: RegisterNumber
    immediate: bytearray

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_load_immediate_32(self)


@attrs.frozen
class LoadImmediate64(MicroOpBase):
    destination: RegisterNumber
    immediate: bytearray

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_load_immediate_64(self)


@attrs.frozen
class StoreRegister(MicroOpBase):
    destination: MemoryAddress
    source: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_store_register(self)


@attrs.frozen
class StoreImmediate8(MicroOpBase):
    destination: MemoryAddress
    immediate: bytearray

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_store_immediate_8(self)


@attrs.frozen
class StoreImmediate16(MicroOpBase):
    destination: MemoryAddress
    immediate: bytearray

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_store_immediate_16(self)


@attrs.frozen
class StoreImmediate32(MicroOpBase):
    destination: MemoryAddress
    immediate: bytearray

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_store_immediate_32(self)


@attrs.frozen
class StoreImmediate64(MicroOpBase):
    destination: MemoryAddress
    immediate: bytearray

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_store_immediate_64(self)


@attrs.frozen
class BinaryArithmeticInt8(MicroOpBase):
    func: BinaryArithmeticFunc
    destination: RegisterNumber
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_binary_arithmetic_int8(self)


@attrs.frozen
class BinaryArithmeticInt16(MicroOpBase):
    func: BinaryArithmeticFunc
    destination: RegisterNumber
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_binary_arithmetic_int16(self)


@attrs.frozen
class BinaryArithmeticInt32(MicroOpBase):
    func: BinaryArithmeticFunc
    destination: RegisterNumber
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_binary_arithmetic_int32(self)


@attrs.frozen
class BinaryArithmeticInt64(MicroOpBase):
    func: BinaryArithmeticFunc
    destination: RegisterNumber
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_binary_arithmetic_int64(self)


@attrs.frozen
class BinaryArithmeticFloat(MicroOpBase):
    func: BinaryArithmeticFunc
    destination: RegisterNumber
    left: RegisterNumber
    right: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_binary_arithmetic_float(self)


@attrs.frozen
class UnaryArithmeticInt8(MicroOpBase):
    func: UnaryArithmeticFunc
    destination: RegisterNumber
    source: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_unary_arithmetic_int8(self)


@attrs.frozen
class UnaryArithmeticInt16(MicroOpBase):
    func: UnaryArithmeticFunc
    destination: RegisterNumber
    source: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_unary_arithmetic_int16(self)


@attrs.frozen
class UnaryArithmeticInt32(MicroOpBase):
    func: UnaryArithmeticFunc
    destination: RegisterNumber
    source: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_unary_arithmetic_int32(self)


@attrs.frozen
class UnaryArithmeticInt64(MicroOpBase):
    func: UnaryArithmeticFunc
    destination: RegisterNumber
    source: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_unary_arithmetic_int64(self)


@attrs.frozen
class UnaryArithmeticFloat(MicroOpBase):
    func: UnaryArithmeticFunc
    destination: RegisterNumber
    source: RegisterNumber

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_unary_arithmetic_float(self)


# !! TEMPORARY !! #
@attrs.frozen
class DumpMemory(MicroOpBase):
    section_id: int

    def accept[R](self, visitor: MicroOpVisitor[R]) -> R:
        return visitor.visit_dump_memory(self)


type LoadMicroOp = (
    LoadAddress | LoadImmediate8 | LoadImmediate16 | LoadImmediate32 | LoadImmediate64
)
type StoreMicroOp = (
    StoreRegister
    | StoreImmediate8
    | StoreImmediate16
    | StoreImmediate32
    | StoreImmediate64
)
type BinaryArithmetic = (
    BinaryArithmeticInt8
    | BinaryArithmeticInt16
    | BinaryArithmeticInt32
    | BinaryArithmeticInt64
    | BinaryArithmeticFloat
)
type UnaryArithmetic = (
    UnaryArithmeticInt8
    | UnaryArithmeticInt16
    | UnaryArithmeticInt32
    | UnaryArithmeticInt64
    | UnaryArithmeticFloat
)
type MicroOp = (
    LoadMicroOp | StoreMicroOp | BinaryArithmetic | UnaryArithmetic | DumpMemory
)
