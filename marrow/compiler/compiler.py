from __future__ import annotations

import io
import time
import typing

from marrow.compiler.backend.macro.ops import DumpHeap
from marrow.compiler.components import Parser
from marrow.compiler.components import Tokenizer
from marrow.compiler.renderers.util import render_memory_location
from marrow.tooling import CompilerTooling

from .resources import CompilerResources

if typing.TYPE_CHECKING:
    from marrow.compiler.common import Expr
    from marrow.compiler.common import IRInstruction
    from marrow.compiler.common import MacroOp
    from marrow.tooling import GlobalTooling


class Compiler:
    def __init__(self, tooling: GlobalTooling, verbose: bool, debug: bool) -> None:
        self.tooling: typing.Final = CompilerTooling.from_global(tooling)

        self.resources = CompilerResources(io.StringIO())

        self.verbose: typing.Final = verbose
        self.debug: typing.Final = debug

        self.log_preparative_setup(
            "parse tree sanity checker",
            *(("parse tree renderer",) if self.debug else ()),
            "SSA IR generator",
            *(("SSA rvalue renderer",) if self.debug else ()),
            "macro op generator",
            *(("macro op renderer",) if self.debug else ()),
        )

        self.tooling.logger.success("compiler initialized")

    def initialize_resources(self, file: typing.TextIO) -> None:
        self.resources = CompilerResources(file)

    def log_preparative_setup(self, *names: str) -> None:
        buffer = io.StringIO()

        print(
            "preparative setup: initialized components that will be used later",
            file=buffer,
        )

        for name in names:
            print(f"• {name}", file=buffer)

        self.tooling.logger.note(buffer.getvalue())

    def make_parse_tree_log(self, parse_tree: Expr) -> str:
        buffer = io.StringIO()

        print("rendering the parse tree", file=buffer)
        print(self.tooling.parse_tree_renderer.render(parse_tree), file=buffer)

        return buffer.getvalue().removesuffix("\n")

    def make_ssa_instructions_log(self, ir: list[IRInstruction]) -> str:
        buffer = io.StringIO()

        for instruction in ir:
            lvalue = render_memory_location(instruction.destination)
            rvalue = self.tooling.rvalue_renderer.render(instruction.rvalue)
            print(f"{lvalue} \x1b[38;2;233;198;175m:=\x1b[39m {rvalue}", file=buffer)

        return buffer.getvalue().removesuffix("\n")

    def make_ssa_ir_generation_log(self, ir: list[IRInstruction]) -> str:
        buffer = io.StringIO()

        print("generated SSA IR", file=buffer)

        if self.debug:
            print(self.make_ssa_instructions_log(ir), file=buffer)

        return buffer.getvalue()

    def make_macro_ops_log(self, macro_ops: list[MacroOp]) -> str:
        buffer = io.StringIO()

        for op in macro_ops:
            print(self.tooling.macro_op_renderer.render(op), file=buffer)

        return buffer.getvalue().removesuffix("\n")

    def make_macro_ops_generation_log(self, macro_ops: list[MacroOp]) -> str:
        buffer = io.StringIO()

        print(f"generated {len(macro_ops)} macro ops", file=buffer)

        if self.debug:
            print(self.make_macro_ops_log(macro_ops), file=buffer)

        return buffer.getvalue()

    def tokenize(self) -> None:
        tokens = Tokenizer(self.resources.file).run()
        self.tooling.logger.info("tokenized source")

        self.resources.tokens = tokens

    def parse(self) -> None:
        parse_tree = Parser(self.resources.tokens, self.tooling).run()
        self.tooling.logger.info("parsed source")

        if self.debug:
            self.tooling.logger.debug(self.make_parse_tree_log(parse_tree))

        self.resources.parse_tree = parse_tree

    def generate_ssa_ir(self) -> None:
        ir = self.tooling.ir_generator.generate(self.resources.parse_tree)
        self.tooling.logger.info(self.make_ssa_ir_generation_log(ir))

        self.resources.ir = ir

    def generate_macro_ops(self) -> None:
        macro_ops = self.tooling.macro_op_generator.generate(self.resources.ir)
        self.tooling.logger.info(self.make_macro_ops_generation_log(macro_ops))

        if self.debug:
            macro_ops.append(DumpHeap(0))
            self.tooling.logger.info("injected memory dump op")

        self.resources.macro_ops = macro_ops

    def compile(self, source: typing.TextIO) -> int:
        self.initialize_resources(source)
        self.tooling.logger.info(
            f"starting compilation of {self.resources.file_name!r}",
        )

        time_start = time.perf_counter()

        self.tokenize()
        self.parse()

        self.resources.file.close()
        self.tooling.logger.note("done with the file - closed")

        is_parse_tree_sane = self.tooling.sanity_checker.is_sane(
            self.resources.parse_tree,
        )
        self.tooling.logger.info("checked parse tree sanity")

        if not is_parse_tree_sane:
            self.tooling.logger.info("found invalid nodes!")

            for node in self.tooling.sanity_checker.invalid_nodes:
                self.tooling.logger.error(
                    node.message,
                    source_path=node.token.file.name,
                )

            return 1

        self.tooling.logger.success("parse tree seems sane")

        self.generate_ssa_ir()
        self.generate_macro_ops()

        time_end = time.perf_counter()

        if self.debug:
            self.tooling.logger.debug(f"compilation time: {time_end - time_start:.4f}s")

        return 0
