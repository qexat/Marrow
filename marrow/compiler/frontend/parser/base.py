# pyright: reportImportCycles = false

from __future__ import annotations

import collections.abc
import typing

from result import Err
from result import Ok
from result import Result

from marrow.compiler.frontend.ast import expr
from marrow.compiler.frontend.parser import subparsers

if typing.TYPE_CHECKING:
    from marrow.compiler.common import Token
    from marrow.compiler.common import TokenType
    from marrow.logger import Logger


class ParserBase:
    """
    Base class for a Pratt parser.

    Children can override `initialize_subparsers` if they wish to add
    subparsers to be used.
    """

    def __init__(self, tokens: collections.abc.Iterator[Token], logger: Logger) -> None:
        self.logger = logger

        self.tokens: typing.Final = tokens
        self.buffer: list[Token] = []

        self.atom_parsers: dict[TokenType, subparsers.AtomSubparser] = {}
        self.prefix_parsers: dict[TokenType, subparsers.PrefixSubparser] = {}
        self.nonprefix_parsers: dict[TokenType, subparsers.NonprefixSubparser] = {}

        self.initialize_subparsers()

    def initialize_subparsers(self) -> None:
        """
        Overridable method to initialize the subparsers.
        """

    @typing.overload
    def register_subparser(
        self,
        type: TokenType,
        subparser: subparsers.AtomSubparser,
    ) -> None: ...
    @typing.overload
    def register_subparser(
        self,
        type: TokenType,
        subparser: subparsers.NonprefixSubparser,
    ) -> None: ...
    @typing.overload
    def register_subparser(
        self,
        type: TokenType,
        subparser: subparsers.PrefixSubparser,
    ) -> None: ...

    def register_subparser(
        self, type: TokenType, subparser: subparsers.Subparser,
    ) -> None:
        """
        Register a subparser for a given token type.

        Parameters
        ----------
        type : TokenType
        subparser : Subparser
        """

        match subparser:
            case subparsers.NonprefixSubparser():
                self.nonprefix_parsers[type] = subparser
            case subparsers.PrefixSubparser():
                self.prefix_parsers[type] = subparser
            case subparsers.AtomSubparser():
                self.atom_parsers[type] = subparser

    def get_precedence(self) -> int:
        """
        Returns
        -------
        int
            The precedence of the binary operator of the expression being
            currently parsed.
        """

        subparser = self.nonprefix_parsers.get(self.peek().type)

        if subparser is None:
            return 0

        return subparser.get_precedence()

    def peek(self, distance: int = 0) -> Token:
        """
        Parameters
        ----------
        distance : int, optional
            The lookahead distance.

        Returns
        -------
        Token
            The current token.
        """

        if distance < 0:
            raise TypeError("distance must be a non-negative integer")

        while distance >= len(self.buffer):
            self.buffer.append(next(self.tokens))

        return self.buffer[distance]

    @typing.overload
    def consume(self) -> Token:
        """
        Consume the current token.

        Returns
        -------
        Token
            The token being consumed.
        """

    @typing.overload
    def consume(self, expected: TokenType) -> Result[Token, str]:
        """
        Consume the current token if its type is the one expected.

        Parameters
        ----------
        expected : TokenType

        Returns
        -------
        Result[Token, str]
            The consumed token, wrapped in `Ok`, or the error message wrapped
            in `Err`.
        """

    def consume(self, expected: TokenType | None = None) -> Token | Result[Token, str]:
        token = self.peek()

        if expected is not None:
            if token.type is not expected:
                return Err(f"expected token {expected!r}, got {token.type!r}")

            return Ok(self.consume())

        return self.buffer.pop(0)

    def match(self, expected: TokenType) -> bool:
        """
        If the current token is of the expected type, consume it.

        Parameters
        ----------
        expected : TokenType

        Returns
        -------
        bool
            Whether the token is of the expected type.
        """

        token = self.peek()

        if token.type is not expected:
            return False

        self.consume()

        return True

    def parse_expr(self, precedence: int = 0) -> expr.Expr:
        """
        Parse an expression by consuming tokens.

        Parameters
        ---------
        precedence : int, optional
            The precedence of the operator of the expression being parsed.
        """

        token = self.consume()
        subparser = self.prefix_parsers.get(
            token.type,
            self.atom_parsers.get(token.type),
        )

        if subparser is None:
            return expr.InvalidExpr(f"unexpected token {token.lexeme!r}", token)

        left = subparser.parse(self, token)

        if isinstance(left, Err):
            return left

        while precedence < self.get_precedence():
            token = self.consume()
            subparser = self.nonprefix_parsers[token.type]

            left = subparser.parse(self, left, token)

        return left

    def run(self) -> expr.Expr:
        """
        Run the parser.

        Returns
        -------
        Expr
            The resulting parsed expression.
        """
        expression = self.parse_expr()

        if self.buffer:
            self.logger.warn(
                f"parser buffer still contains {len(self.buffer)} token(s)",
            )

        return expression
