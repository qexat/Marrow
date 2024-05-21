import collections.abc
import io
import typing

from .token import FileProxy
from .token import Span
from .token import Token
from .token_type import KEYWORD_LEXEMES
from .token_type import TokenType


class Tokenizer:
    """
    The tokenizer transforms a file containing source code into tokens.
    It is lazy, only yielding tokens when needed.
    """

    def __init__(self, file: typing.TextIO) -> None:
        self.file: typing.Final = file
        self.file_name: typing.Final[str] = (
            self.file.name if hasattr(self.file, "name") else "<string>"
        )

        self.buffer: list[str] = []
        self.read = io.StringIO()

        self.start = self.current = 0

    def is_at_end(self) -> bool:
        """
        Returns
        -------
        bool
            `True` if the tokenizer is at the end of the file, else `False`.
        """

        return self.peek() == "\0"

    def peek(self, distance: int = 0, /) -> str:
        """
        Return the character at `distance` of the current character, without
        consuming it.

        Parameters
        ----------
        distance : int, optional
            The lookahead distance.

        Returns
        -------
        str
            The peeked character.
        """

        if distance < 0:
            raise ValueError("n must be positive")

        while distance >= len(self.buffer):
            char = self.file.read(1)

            self.read.write(char)
            self.buffer.append(char or "\0")

        return self.buffer[distance]

    def sync_head(self) -> None:
        """Prepare `start` for a new token."""

        self.start = self.current

    def advance(self, steps: int = 1, /) -> None:
        """
        Advance the head by `steps` (default: 1).

        Parameters
        ----------
        steps : int, optional
            The number of steps to advance.

        Raises
        ------
        ValueError
            If `steps` is equal to 0.
        """

        if steps == 0:
            raise ValueError("steps must be non-zero")

        self.current += 1

    def consume(self) -> str:
        """
        Consume the current character.

        Returns
        -------
        str
            The consumed character.
        """

        _ = self.peek()
        self.advance()

        return self.buffer.pop(0)

    # TODO: support non-decimal bases (binary, hexadecimal)
    def scan_number(self) -> TokenType:
        """
        Scan a number token while it can.

        First, scan digits. If no period is found, it is an integer.
        Else, delegate the rest of the scan of the float.

        Returns
        -------
        TokenType
            The float token type if a period was found, else the integer token type.
        """

        while self.peek().isdecimal():
            self.consume()

        if self.peek() == ".":
            self.consume()

            return self.scan_float_decimals()

        return TokenType.INTEGER

    def scan_float_decimals(self) -> TokenType:
        """
        Scan the rest of the float token.

        Should not be called directly - intended to be used by `scan_number`.

        Returns
        -------
        TokenType
            The float token type.
        """

        while self.peek().isdecimal():
            self.consume()

        return TokenType.FLOAT

    def scan_symbol(self) -> TokenType:
        """
        Scan a symbol token while it can.

        Returns
        -------
        TokenType
            The corresponding keyword token type, or the invalid token type.
        """

        while self.peek().isalnum():
            self.consume()

        return KEYWORD_LEXEMES.get(self.get_lexeme(), TokenType.INVALID)

    def scan_token(self) -> TokenType:
        """
        Consume characters until a token is formed.

        Returns
        -------
        TokenType
            The type of the formed token.
        """

        token_type: TokenType | None = None

        while token_type is None:
            char = self.consume()

            match char:
                case "\0":
                    token_type = TokenType.EOF
                case " " | "\t" | "\r" | "\n":
                    self.sync_head()
                case "(":
                    token_type = TokenType.LEFT_PAREN
                case ")":
                    token_type = TokenType.RIGHT_PAREN
                case "-":
                    token_type = TokenType.MINUS
                case "%":
                    token_type = TokenType.PERCENT
                case "+":
                    token_type = TokenType.PLUS
                case "/":
                    token_type = TokenType.SLASH
                case "*":
                    token_type = TokenType.STAR
                case ";":
                    token_type = TokenType.SEMICOLON
                case _ if char.isdecimal():
                    token_type = self.scan_number()
                case _ if char.isalpha():
                    token_type = self.scan_symbol()
                case _:
                    token_type = TokenType.INVALID

        return token_type

    def get_lexeme(self) -> str:
        """
        Returns
        -------
        str
            The lexeme of the currently scanned token.
        """

        return self.read.getvalue()[self.start : self.current]

    def build_token(self, token_type: TokenType) -> Token:
        """
        Parameters
        ----------
        token_type : TokenType

        Returns
        -------
        Token
            The token object from the obtained token type and lexeme.
        """

        return Token(
            token_type,
            self.get_lexeme(),
            Span(self.start, self.current),
            FileProxy(self.file_name, self.read),
        )

    def run(self) -> collections.abc.Generator[Token, None, None]:
        """
        Core of the tokenizer.

        Yields
        ------
        Token
            The token that has been produced.
        """

        while not self.is_at_end():
            self.sync_head()

            yield self.build_token(self.scan_token())

        while True:
            yield self.build_token(TokenType.EOF)
