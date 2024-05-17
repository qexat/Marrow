# pyright: reportUnusedCallResult = false

import argparse
import tempfile
import typing


class FakeFileType:
    def __init__(
        self,
        mode: str,
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> None:
        self._mode = mode
        self._buffering = buffering
        self._encoding = encoding
        self._errors = errors

    def __call__(self, source: str) -> typing.TextIO:
        file: tempfile.SpooledTemporaryFile[str] = tempfile.SpooledTemporaryFile(
            mode=self._mode,
            buffering=self._buffering,
            encoding=self._encoding,
            errors=self._errors,
        )

        file.write(source)
        file.seek(0)

        return file  # pyright: ignore[reportReturnType]


class CLIParser:
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()
        self.subparsers = self._parser.add_subparsers(dest="command", required=True)

    def _add_file_or_string_group(
        self,
        parser: argparse.ArgumentParser,
        verb: str,
    ) -> None:
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument(
            "--file",
            "-f",
            type=argparse.FileType("r"),
            help=f"the marrow file to {verb}",
            metavar="path",
            dest="source",
        )
        source_group.add_argument(
            "--string",
            "-s",
            type=FakeFileType("r"),
            help=f"the string to {verb}",
            metavar="source",
            dest="source",
        )

    def get_compile_parser(self) -> argparse.ArgumentParser:
        parser = self.subparsers.add_parser(
            "compile",
            help="compile marrow code without running it",
        )

        self._add_file_or_string_group(parser, "compile")

        return parser

    def get_run_parser(self) -> argparse.ArgumentParser:
        parser = self.subparsers.add_parser("run", help="run marrow code")

        self._add_file_or_string_group(parser, "run")

        return parser

    def get_parser(self) -> argparse.ArgumentParser:
        self._parser.add_argument(
            "--verbose",
            "-vb",
            action="store_true",
            help="show in detail what is going on",
        )
        self._parser.add_argument(
            "--debug",
            "-d",
            action="store_true",
            help="get debugging information",
        )

        return self._parser

    def parse_args(self, args: list[str] | None = None) -> argparse.Namespace:
        self.get_parser()
        self.get_compile_parser()
        self.get_run_parser()

        return self._parser.parse_args(args)
