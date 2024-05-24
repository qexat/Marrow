import argparse
import io
import sys
import typing

from marrow.compiler import Compiler
from marrow.endec import EnDec
from marrow.logger import Logger
from marrow.runtime import Machine


class Environment:
    def __init__(self, *, verbose: bool, debug: bool) -> None:
        self.verbose: typing.Final = verbose
        self.debug: typing.Final = debug

        self.logger: typing.Final = Logger(verbose=self.verbose)
        self.encoder_decoder: typing.Final = EnDec()
        self.compiler: typing.Final = Compiler(
            self.logger,
            self.encoder_decoder,
            self.verbose,
            self.debug,
        )
        self.machine: typing.Final = Machine(self.logger, self.encoder_decoder)

        self.logger.info(
            self.make_setup_log(
                "logger",
                "encoder/decoder",
                "compiler",
                "machine",
            ),
        )
        self.logger.success("marrow environment initialized")

    @classmethod
    def from_args(cls, namespace: argparse.Namespace) -> typing.Self:
        return cls(
            verbose=namespace.verbose,
            debug=namespace.debug,
        )

    def make_setup_log(self, *names: str) -> str:
        buffer = io.StringIO()

        print("set up components", file=buffer)

        for name in names:
            print(f"• {name}", file=buffer)

        return buffer.getvalue()

    def compile(self, source: typing.TextIO) -> int:
        exit_code = self.compiler.compile(source)

        if exit_code > 0:
            self.logger.error("errors occurred - aborting")

        return exit_code

    def run(self, source: typing.TextIO) -> int:
        exit_code = self.compiler.compile(source)

        if exit_code > 0:
            return exit_code

        self.machine.execute(self.compiler.resources.macro_ops, debug=self.debug)
        self.logger.info("execution finished")

        return 0

    def shell(self) -> int:
        if sys.platform == "linux":
            __import__("readline")

        self.logger.banner("Marrow Shell - press Ctrl+C to exit")

        exit_code = 0

        while True:
            try:
                source_string = input("\x1b[95m>>>\x1b[39m ")
            except (KeyboardInterrupt, EOFError):
                break
            else:
                if not source_string:
                    continue

                source = io.StringIO(source_string)

                if self.compiler.compile(source) == 0:
                    self.machine.execute(
                        self.compiler.resources.macro_ops,
                        debug=self.debug,
                    )

        return exit_code
