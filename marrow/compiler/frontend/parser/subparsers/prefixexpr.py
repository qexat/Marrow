from __future__ import annotations

import abc
import typing

from marrow.compiler.frontend.ast import expr

if typing.TYPE_CHECKING:
    from marrow.compiler.common import Token
    from marrow.compiler.common import UnaryOpTokenType
    from marrow.compiler.frontend.parser.base import ParserBase


class PrefixSubparser(abc.ABC):
    """Parser for prefix expressions."""

    @abc.abstractmethod
    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        pass


class UnaryPrefixSubparser(PrefixSubparser):
    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        operand = parser.parse_expr()

        return expr.UnaryExpr(typing.cast("UnaryOpTokenType", token.type), operand)
