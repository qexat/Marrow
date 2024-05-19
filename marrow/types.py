"""
Types that are used by both the compiler and the runtime.
"""

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
