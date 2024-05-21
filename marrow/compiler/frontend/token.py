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

    def get_lines(self) -> list[str]:
        contents = self.file.contents.getvalue()
        (_, start), (_, end) = self.get_line_span()

        return [line for line in contents.splitlines(keepends=True)[start - 1 : end]]

    def get_line_span(self) -> tuple[tuple[int, int], tuple[int, int]]:
        contents = self.file.contents.getvalue()

        start_line_offset = self.span.start
        end_line_offset = self.span.end

        for index, char in enumerate(reversed(contents[: self.span.start])):
            if char == "\n":
                start_line_offset = self.span.start - index
                break

        for index, char in enumerate(reversed(contents[: self.span.end])):
            if char == "\n":
                end_line_offset = self.span.end - index
                break

        line_start = len(contents[:start_line_offset].splitlines())
        line_end = len(contents[:end_line_offset].splitlines())

        return (
            (self.span.start - start_line_offset + 1, line_start + 1),
            (self.span.end - end_line_offset + 1, line_end + 1),
        )
