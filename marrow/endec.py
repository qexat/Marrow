"""
ENcoder/DECoder of bytecode immediate values.
"""

from __future__ import annotations

import struct
import typing

from marrow.types import ImmediateType

if typing.TYPE_CHECKING:
    from marrow.types import RuntimeType


BYTE_ORDER_CHAR = ">"
INTEGER_FORMAT_CHAR = "Q"
FLOAT_FORMAT_CHAR = "d"

INTEGER_FORMAT = BYTE_ORDER_CHAR + INTEGER_FORMAT_CHAR
FLOAT_FORMAT = BYTE_ORDER_CHAR + FLOAT_FORMAT_CHAR

INTEGER_MASK = 0xFF_FF_FF_FF_FF_FF_FF_FF  # 2**64 - 1


# TODO: handle signed integers
class EncoderDecoder:
    def encode_immediate(
        self,
        value: RuntimeType,
        *,
        truncate: bool = True,
    ) -> bytearray:
        match value:
            case int():
                return self.encode_integer(value, truncate=truncate)
            case float():
                return self.encode_float(value)

    def encode_integer(self, value: int, *, truncate: bool = True) -> bytearray:
        if truncate:
            value = self.truncate_integer(value)

        packed = bytearray(8)
        struct.pack_into(INTEGER_FORMAT, packed, 0, value)

        return packed

    def encode_float(self, value: float) -> bytearray:
        packed = bytearray(8)
        struct.pack_into(FLOAT_FORMAT, packed, 0, value)

        return packed

    def decode_immediate(self, value: bytearray, type: ImmediateType) -> RuntimeType:
        match type:
            case ImmediateType.INTEGER:
                return self.decode_integer(value)
            case ImmediateType.FLOAT:
                return self.decode_float(value)

    def decode_integer(self, value: bytearray) -> int:
        result, *_ = struct.unpack_from(INTEGER_FORMAT, value)

        return result

    def decode_float(self, value: bytearray) -> float:
        result, *_ = struct.unpack_from(FLOAT_FORMAT, value)

        return result

    def does_integer_overflow(self, value: int) -> bool:
        return value != self.truncate_integer(value)

    def truncate_integer(self, value: int) -> int:
        return value & INTEGER_MASK
