from __future__ import annotations

import abc
import typing

from result import Err

from marrow.compiler.common import LiteralTokenType
from marrow.compiler.common import TokenType
from marrow.compiler.frontend.ast import expr

if typing.TYPE_CHECKING:
    from marrow.compiler.common import Token
    from marrow.compiler.frontend.parser.base import ParserBase


class AtomSubparser(abc.ABC):
    """Interface representing a parser for an atomic expression."""

    @abc.abstractmethod
    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        """
        Parameters
        ----------
        parser : ParserBase
            The parser which the subparser is registered in.
        token : Token
            The token of the atom.

        Returns
        -------
        Expr
            The parsed expression.
        """


class BlockSubparser(AtomSubparser):
    """Parser for block expressions."""

    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        expr_list: list[expr.Expr] = []

        while parser.peek().type not in {TokenType.END, TokenType.EOF}:
            expr_list.append(parser.parse_expr())

            if (parser.peek()).type is not TokenType.END and isinstance(
                parser.consume(TokenType.SEMICOLON),
                Err,
            ):
                current_token = parser.peek()
                expr_list.append(
                    expr.InvalidExpr(
                        f"expected ';' after {current_token.type.name}",
                        current_token,
                        [],
                    ),
                )

        if isinstance(parser.consume(TokenType.END), Err):
            return expr.InvalidExpr("missing expected 'end'", token, expr_list)

        return expr.BlockExpr(expr_list)


class GroupingSubparser(AtomSubparser):
    """Parser for grouping expressions."""

    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        expression = parser.parse_expr()

        if isinstance(parser.consume(TokenType.RIGHT_PAREN), Err):
            return expr.InvalidExpr("missing expected ')'", token, [expression])

        return expr.GroupingExpr(expression)


class LiteralScalarSubparser(AtomSubparser):
    """Parser for literal scalar expressions."""

    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        return expr.LiteralScalarExpr(token, typing.cast(LiteralTokenType, token.type))


class ModSubparser(AtomSubparser):
    """Parser for module expressions."""

    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        return expr.ModExpr(parser.parse_expr())
