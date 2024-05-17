import enum
import typing


class TokenType(enum.Enum):
    END = enum.auto()
    IN = enum.auto()
    MOD = enum.auto()

    FLOAT = enum.auto()
    INTEGER = enum.auto()

    LEFT_PAREN = enum.auto()
    RIGHT_PAREN = enum.auto()

    MINUS = enum.auto()
    PERCENT = enum.auto()
    PLUS = enum.auto()
    SLASH = enum.auto()
    STAR = enum.auto()

    SEMICOLON = enum.auto()

    INVALID = enum.auto()
    EOF = enum.auto()


type KeywordTokenType = typing.Literal[TokenType.END, TokenType.IN, TokenType.MOD]
type LiteralTokenType = typing.Literal[TokenType.FLOAT, TokenType.INTEGER]

type AtomTokenType = KeywordTokenType | LiteralTokenType
type BinaryOpTokenType = typing.Literal[
    TokenType.MINUS, TokenType.PERCENT, TokenType.PLUS, TokenType.SLASH, TokenType.STAR,
]
type PunctuationTokenType = typing.Literal[TokenType.SEMICOLON]
type UnaryOpTokenType = typing.Literal[TokenType.MINUS, TokenType.PLUS]

KEYWORD_LEXEMES: dict[str, KeywordTokenType] = {
    "end": TokenType.END,
    "in": TokenType.IN,
    "mod": TokenType.MOD,
}
