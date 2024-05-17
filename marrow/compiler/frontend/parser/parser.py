import typing

from marrow.compiler.common import TokenType

from .base import ParserBase
from .precedence import Precedence
from .subparsers.atomexpr import BlockSubparser
from .subparsers.atomexpr import GroupingSubparser
from .subparsers.atomexpr import LiteralScalarSubparser
from .subparsers.atomexpr import ModSubparser
from .subparsers.nonprefixexpr import BinaryNonprefixSubparser
from .subparsers.prefixexpr import UnaryPrefixSubparser


class Parser(ParserBase):
    """The actual parser."""

    @typing.override
    def initialize_subparsers(self) -> None:
        self.register_subparser(TokenType.INTEGER, LiteralScalarSubparser())
        self.register_subparser(TokenType.FLOAT, LiteralScalarSubparser())
        self.register_subparser(TokenType.LEFT_PAREN, GroupingSubparser())

        self.register_subparser(TokenType.IN, BlockSubparser())
        self.register_subparser(TokenType.MOD, ModSubparser())

        self.register_subparser(TokenType.PLUS, UnaryPrefixSubparser())
        self.register_subparser(TokenType.MINUS, UnaryPrefixSubparser())

        self.register_subparser(
            TokenType.PLUS, BinaryNonprefixSubparser(Precedence.ADDITION),
        )
        self.register_subparser(
            TokenType.MINUS, BinaryNonprefixSubparser(Precedence.SUBTRACTION),
        )
        self.register_subparser(
            TokenType.STAR, BinaryNonprefixSubparser(Precedence.MULTIPLICATION),
        )
        self.register_subparser(
            TokenType.SLASH, BinaryNonprefixSubparser(Precedence.DIVISION),
        )
        self.register_subparser(
            TokenType.PERCENT, BinaryNonprefixSubparser(Precedence.REMAINDER),
        )
