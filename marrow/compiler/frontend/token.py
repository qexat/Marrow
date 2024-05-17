import io
import typing

from .token_type import TokenType


class Span(typing.NamedTuple):
    """
    Represent the span of a token, i.e. its offset in the source.
    """

    start: int
    end: int


class FileProxy(typing.NamedTuple):
    """
    Proxy of the file from which the source comes from.

    Since the source might come from a string (e.g. in the REPL), it is a
    needed abstraction to still be able to treat it like a file. In that case,
    `name` is `<string>`.
    """

    name: str
    contents: io.StringIO


class Token(typing.NamedTuple):
    """
    Record representing a token.

    Attributes
    ----------
    type : TokenType
        The type of the token.
    lexeme : str
        The portion of the source corresponding to the token.
    span : Span
        The position of the token in the source.
    file : FileProxy
        The file from which the token is from.
    """

    type: TokenType
    lexeme: str
    span: Span
    file: FileProxy
