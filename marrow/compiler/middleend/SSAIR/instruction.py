import typing

from marrow.compiler.types import MemoryLocation

from .rvalue import AtomicRValue
from .rvalue import BinaryRValue
from .rvalue import RValue
from .rvalue import UnaryRValue


class IRInstruction(typing.NamedTuple):
    destination: MemoryLocation
    rvalue: RValue

    def is_dependent_on(self, location: MemoryLocation) -> bool:
        match self.rvalue:
            case AtomicRValue(_):
                return False
            case BinaryRValue(_, left, right):
                return location == left or location == right
            case UnaryRValue(_, right):
                return location == right
