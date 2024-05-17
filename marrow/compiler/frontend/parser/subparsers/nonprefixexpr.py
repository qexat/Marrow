from __future__ import annotations

import abc
import typing

import attrs

from marrow.compiler.frontend.ast import expr

if typing.TYPE_CHECKING:
    from marrow.compiler.common import BinaryOpTokenType
    from marrow.compiler.common import Token
    from marrow.compiler.frontend.parser.base import ParserBase


class NonprefixSubparser(abc.ABC):
    """Parser for non-prefix expressions, such as binary infix."""

    precedence: int

    @abc.abstractmethod
    def get_precedence(self) -> int:
        """
        Returns
        -------
        int
            The precedence of the expression operator.
        """

    @abc.abstractmethod
    def parse(self, parser: ParserBase, left: expr.Expr, token: Token) -> expr.Expr:
        """
        Parameters
        ----------
        parser : ParserBase
            The parser which the subparser is registered in.
        left : Expr
            The left side of the expression.
        token : Token
            The operator token.

        Returns
        -------
        Expr
            The parsed expression.
        """


@attrs.frozen
class BinaryNonprefixSubparser(NonprefixSubparser):
    """Parser for binary expressions."""

    precedence: int
    is_right_associative: bool = False

    def get_precedence(self) -> int:
        return self.precedence

    def parse(self, parser: ParserBase, left: expr.Expr, token: Token) -> expr.Expr:
        right = parser.parse_expr(self.precedence - self.is_right_associative)

        return expr.BinaryExpr(
            typing.cast("BinaryOpTokenType", token.type),
            left,
            right,
        )
