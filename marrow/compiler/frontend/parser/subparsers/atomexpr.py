from __future__ import annotations

import abc
import io
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

    def _make_float_warning_message(self, token: Token) -> str:
        buffer = io.StringIO()

        print(
            "float literals are valid, but floats are not supported by the runtime yet",
            file=buffer,
        )

        (row_start, line_start), (row_end, line_end) = token.get_line_span()

        row_start -= 1
        row_end -= 1

        in_token = False

        # TODO: proper diagnostician
        for line_no, line in enumerate(token.get_lines(), start=line_start):
            buffer.write(f"\x1b[2m{line_no:>4} | \x1b[22m")

            if line_no == line_start:
                buffer.write(line[:row_start])
                buffer.write("\x1b[1;93m")

                if line_start == line_end:
                    buffer.write(line[row_start:row_end])
                    buffer.write("\x1b[22;39m")
                    buffer.write(line[row_end:])
                else:
                    buffer.write(line[row_start:])
                    in_token = True

            elif line_no == line_end:
                buffer.write(line[:row_end])
                buffer.write("\x1b[22;39m")
                buffer.write(line[row_end:])

            elif in_token:
                buffer.write("\x1b[1;93m")

        return buffer.getvalue()

    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        if token.type is TokenType.FLOAT:
            row_start, line_start = token.get_line_span()[0]

            parser.tooling.logger.warn(
                self._make_float_warning_message(token),
                source_path=f"{token.file.name}:{line_start}:{row_start}",
            )

        return expr.LiteralScalarExpr(token, typing.cast(LiteralTokenType, token.type))


class ModSubparser(AtomSubparser):
    """Parser for module expressions."""

    def parse(self, parser: ParserBase, token: Token) -> expr.Expr:
        return expr.ModExpr(parser.parse_expr())
