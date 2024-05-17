import enum
import io
import sys
import typing

import anstrip
import attrs

Symbol: typing.TypeAlias = typing.Literal["!", "?", "*", "i", "✓"]


class Printer(typing.Protocol):
    def __call__(
        self,
        *values: object,
        sep: str | None = None,
        end: str | None = None,
        file: typing.TextIO | None = None,
    ) -> typing.Any: ...


@attrs.frozen
class LogKindData:
    symbol: Symbol
    color: int
    default_output: typing.TextIO
    bypasses_verbosity: bool = attrs.field(kw_only=True, default=False)


class LogKind(enum.Enum):
    ERROR = LogKindData("!", 9, sys.stderr, bypasses_verbosity=True)
    SUCCESS = LogKindData("✓", 10, sys.stdout)
    WARNING = LogKindData("!", 11, sys.stderr, bypasses_verbosity=True)
    INFO = LogKindData("i", 12, sys.stdout)
    NOTE = LogKindData("*", 13, sys.stdout)
    DEBUG = LogKindData("?", 14, sys.stdout, bypasses_verbosity=True)


class Logger:
    MAIN_TEMPLATE = "\x1b[38;5;{}m<\x1b[1m{}\x1b[22m>\x1b[39m {}"
    SECONDARY_TEMPLATE = " \x1b[38;5;{}m│\x1b[39m  {}"

    def __init__(self, *, verbose: bool = False, force_colors: bool = False) -> None:
        self.verbose = verbose
        self.force_colors = force_colors

    @property
    def printer(self) -> Printer:
        return print if self.force_colors else anstrip.print

    def get_message(self, kind: LogKind, message: str) -> str:
        buffer = io.StringIO()
        main, *secondary = message.splitlines()

        print(
            self.MAIN_TEMPLATE.format(kind.value.color, kind.value.symbol, main),
            file=buffer,
        )

        for line in secondary:
            print(self.SECONDARY_TEMPLATE.format(kind.value.color, line), file=buffer)

        return buffer.getvalue().removesuffix("\n")

    def log(
        self,
        kind: LogKind,
        message: str,
        *,
        file: typing.TextIO | None = None,
    ) -> None:
        if not self.verbose and not kind.value.bypasses_verbosity:
            return

        _file = file or kind.value.default_output
        self.printer(self.get_message(kind, message), file=_file)

    def error(self, message: str) -> None:
        self.log(LogKind.ERROR, message)

    def success(self, message: str) -> None:
        self.log(LogKind.SUCCESS, message)

    def warn(self, message: str) -> None:
        self.log(LogKind.WARNING, message)

    def info(self, message: str) -> None:
        self.log(LogKind.INFO, message)

    def note(self, message: str) -> None:
        self.log(LogKind.NOTE, message)

    def debug(self, message: str) -> None:
        color = LogKind.DEBUG.value.color
        self.log(LogKind.DEBUG, f"\x1b[38;5;{color}m[debug]\x1b[39m {message}")
