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

        self._global_flags_parent = self.get_global_flags_parent()
        self._source_parent = self.get_source_parent()

    def get_global_flags_parent(self) -> argparse.ArgumentParser:
        parent = argparse.ArgumentParser(add_help=False)
        parent.add_argument(
            "--verbose",
            "--wordy",
            "-w",
            action="store_true",
            help="show in detail what is going on",
        )
        parent.add_argument(
            "--debug",
            "-d",
            action="store_true",
            help="get debugging information",
        )

        return parent

    def get_source_parent(self) -> argparse.ArgumentParser:
        parent = argparse.ArgumentParser(add_help=False)
        parent.add_argument(
            "source",
            nargs="?",
            type=argparse.FileType("r"),
            help="the marrow file to process",
            metavar="path",
        )

        return parent

    def get_compile_parser(self) -> argparse.ArgumentParser:
        parser = self.subparsers.add_parser(
            "compile",
            help="compile marrow code without running it",
            parents=[self._global_flags_parent, self._source_parent],
        )

        return parser

    def get_run_parser(self) -> argparse.ArgumentParser:
        parser = self.subparsers.add_parser(
            "run",
            help="run marrow code",
            parents=[self._global_flags_parent, self._source_parent],
        )

        return parser

    def get_parser(self) -> argparse.ArgumentParser:
        return self._parser

    def parse_args(self, args: list[str] | None = None) -> argparse.Namespace:
        self.get_parser()
        self.get_compile_parser()
        self.get_run_parser()

        return self._parser.parse_args(args)
