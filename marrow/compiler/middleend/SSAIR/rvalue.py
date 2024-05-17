from __future__ import annotations

import abc
import typing

import attrs

if typing.TYPE_CHECKING:
    from marrow.compiler.common import BinaryOpTokenType
    from marrow.compiler.common import Token
    from marrow.compiler.common import UnaryOpTokenType
    from marrow.compiler.types import MemoryLocation


class RValueVisitor[R_co](typing.Protocol):
    def visit_atomic_rvalue(self, value: AtomicRValue) -> R_co: ...
    def visit_binary_rvalue(self, value: BinaryRValue) -> R_co: ...
    def visit_unary_rvalue(self, value: UnaryRValue) -> R_co: ...


class RValueBase(abc.ABC):
    @abc.abstractmethod
    def accept[R](self, visitor: RValueVisitor[R]) -> R:
        pass


@attrs.frozen
class AtomicRValue(RValueBase):
    token: Token

    def accept[R](self, visitor: RValueVisitor[R]) -> R:
        return visitor.visit_atomic_rvalue(self)


@attrs.frozen
class BinaryRValue(RValueBase):
    kind: BinaryOpTokenType
    left: MemoryLocation
    right: MemoryLocation

    def accept[R](self, visitor: RValueVisitor[R]) -> R:
        return visitor.visit_binary_rvalue(self)


@attrs.frozen
class UnaryRValue(RValueBase):
    kind: UnaryOpTokenType
    right: MemoryLocation

    def accept[R](self, visitor: RValueVisitor[R]) -> R:
        return visitor.visit_unary_rvalue(self)


type RValue = AtomicRValue | BinaryRValue | UnaryRValue
