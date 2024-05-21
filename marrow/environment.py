import argparse
import io
import typing

from marrow.compiler import Compiler
from marrow.logger import Logger
from marrow.runtime import Machine
from marrow.runtime.endec import EnDec


class Environment:
    def __init__(
        self,
        *,
        source: typing.TextIO,
        verbose: bool,
        debug: bool,
    ) -> None:
        self.source: typing.Final = source
        self.verbose: typing.Final = verbose
        self.debug: typing.Final = debug

        self.logger: typing.Final = Logger(verbose=self.verbose)
        self.encoder_decoder: typing.Final = EnDec()
        self.compiler: typing.Final = Compiler(
            self.logger,
            self.encoder_decoder,
            self.source,
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
            source=namespace.source,
            verbose=namespace.verbose,
            debug=namespace.debug,
        )

    def make_setup_log(self, *names: str) -> str:
        buffer = io.StringIO()

        print("setup components", file=buffer)

        for name in names:
            print(f"• {name}", file=buffer)

        return buffer.getvalue()

    def compile(self) -> int:
        return self.compiler.compile()

    def run(self) -> int:
        exit_code = self.compiler.compile()

        if exit_code > 0:
            return exit_code

        self.machine.execute(self.compiler.resources.bytecode, debug=self.debug)
        self.logger.info("execution finished")

        return 0
