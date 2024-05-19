from __future__ import annotations

import typing

from .rvalue import AtomicRValue
from .rvalue import BinaryRValue
from .rvalue import UnaryRValue

if typing.TYPE_CHECKING:
    from marrow.types import MemoryAddress

    from .rvalue import RValue


class IRInstruction(typing.NamedTuple):
    destination: MemoryAddress
    rvalue: RValue

    def is_dependent_on(self, location: MemoryAddress) -> bool:
        match self.rvalue:
            case AtomicRValue(_):
                return False
            case BinaryRValue(_, left, right):
                return location == left or location == right
            case UnaryRValue(_, right):
                return location == right
