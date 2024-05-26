# pyright: reportImportCycles = false

from __future__ import annotations

import enum
import typing

from marrow.compiler.common import TokenType

if typing.TYPE_CHECKING:
    from marrow.compiler.frontend.token_type import BinaryOpTokenType
    from marrow.compiler.frontend.token_type import UnaryOpTokenType


class BinaryArithmeticFunc(enum.IntEnum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MOD = enum.auto()


class UnaryArithmeticFunc(enum.IntEnum):
    POS = enum.auto()
    NEG = enum.auto()


BINOP_FUNC_MAPPING: dict[BinaryOpTokenType, BinaryArithmeticFunc] = {
    TokenType.MINUS: BinaryArithmeticFunc.SUB,
    TokenType.PERCENT: BinaryArithmeticFunc.MOD,
    TokenType.PLUS: BinaryArithmeticFunc.ADD,
    TokenType.SLASH: BinaryArithmeticFunc.DIV,
    TokenType.STAR: BinaryArithmeticFunc.MUL,
}

UNOP_FUNC_MAPPING: dict[UnaryOpTokenType, UnaryArithmeticFunc] = {
    TokenType.MINUS: UnaryArithmeticFunc.NEG,
    TokenType.PLUS: UnaryArithmeticFunc.POS,
}
