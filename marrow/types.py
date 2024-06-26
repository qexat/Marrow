"""
Types that are used by both the compiler and the runtime.
"""

import enum
import typing

type RegisterNumber = typing.Literal[
    0x0,
    0x1,
    0x2,
    0x3,
    0x4,
    0x5,
    0x6,
    0x7,
    0x8,
    0x9,
    0xA,
    0xB,
    0xC,
    0xD,
    0xE,
    0xF,
]
type MemoryAddress = int
"""
Memory address.

---
"""
type ByteCount = int


class ImmediateType(enum.IntEnum):
    INTEGER = enum.auto()
    FLOAT = enum.auto()


TYPE_SIZE_MAPPING: dict[ImmediateType, ByteCount] = {
    ImmediateType.INTEGER: 8,
    ImmediateType.FLOAT: 8,
}

# floats are actually disabled while we don't have micro-ops
type RuntimeType = int | float
