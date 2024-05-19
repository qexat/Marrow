"""
Register Access Tracker
"""

from __future__ import annotations

import abc
import typing

import attrs

if typing.TYPE_CHECKING:
    from marrow.types import RegisterNumber


class AccessVisitor[R_co](typing.Protocol):
    def visit_read_access(self, access: ReadAccess) -> R_co: ...
    def visit_write_access(self, access: WriteAccess) -> R_co: ...


@attrs.frozen
class AccessBase(abc.ABC):
    number: RegisterNumber

    @abc.abstractmethod
    def accept[R](self, visitor: AccessVisitor[R]) -> R:
        pass


@attrs.frozen
class ReadAccess(AccessBase):
    def accept[R](self, visitor: AccessVisitor[R]) -> R:
        return visitor.visit_read_access(self)


@attrs.frozen
class WriteAccess(AccessBase):
    value: bytearray

    def accept[R](self, visitor: AccessVisitor[R]) -> R:
        return visitor.visit_write_access(self)


type Access = ReadAccess | WriteAccess
