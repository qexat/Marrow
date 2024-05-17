from __future__ import annotations

import io
import time
import typing

from marrow.compiler.backend.instruction import DumpMemory
from marrow.compiler.components import BytecodeGenerator
from marrow.compiler.components import IRGenerator
from marrow.compiler.components import Parser
from marrow.compiler.components import ParseTreeSanityChecker
from marrow.compiler.components import Tokenizer
from marrow.compiler.renderers import BytecodeRenderer
from marrow.compiler.renderers import ParseTreeRenderer
from marrow.compiler.renderers import RValueRenderer
from marrow.compiler.renderers.util import render_memory_location
from marrow.logger import Logger

from .resources import CompilerResources

if typing.TYPE_CHECKING:
    from marrow.compiler.common import Expr
    from marrow.compiler.common import Instruction
    from marrow.compiler.common import IRInstruction


class Compiler:
    def __init__(
        self,
        logger: Logger,
        file: typing.TextIO,
        verbose: bool,
        debug: bool,
    ) -> None:
        self.logger: typing.Final = logger

        self.resources: typing.Final = CompilerResources(file)

        self.verbose: typing.Final = verbose
        self.debug: typing.Final = debug

        self.sanity_checker: typing.Final = ParseTreeSanityChecker()
        self.parse_tree_renderer: typing.Final = ParseTreeRenderer()
        self.ir_generator: typing.Final = IRGenerator()
        self.rvalue_renderer: typing.Final = RValueRenderer()
        self.instruction_renderer: typing.Final = BytecodeRenderer()
        self.bytecode_generator: typing.Final = BytecodeGenerator(self.logger)

        self.log_preparative_setup(
            "parse tree sanity checker",
            *(("parse tree renderer",) if self.debug else ()),
            "SSA IR generator",
            *(("SSA rvalue renderer",) if self.debug else ()),
            "bytecode generator",
            *(("bytecode renderer",) if self.debug else ()),
        )

        self.logger.success("compiler initialized")

    def get_file_name(self) -> str:
        return self.resources.file.name or "<string>"

    def log_preparative_setup(self, *names: str) -> None:
        buffer = io.StringIO()

        print(
            "preparative setup: initialized components that will be used later",
            file=buffer,
        )

        for name in names:
            print(f"• {name}", file=buffer)

        self.logger.note(buffer.getvalue())

    def make_parse_tree_log(self, parse_tree: Expr) -> str:
        buffer = io.StringIO()

        print("rendering the parse tree", file=buffer)
        print(self.parse_tree_renderer.render(parse_tree), file=buffer)

        return buffer.getvalue().removesuffix("\n")

    def make_ssa_instructions_log(self, ir: list[IRInstruction]) -> str:
        buffer = io.StringIO()

        for instruction in ir:
            lvalue = render_memory_location(instruction.destination)
            rvalue = self.rvalue_renderer.render(instruction.rvalue)
            print(f"{lvalue} \x1b[38;2;233;198;175m:=\x1b[39m {rvalue}", file=buffer)

        return buffer.getvalue().removesuffix("\n")

    def make_ssa_ir_generation_log(self, ir: list[IRInstruction]) -> str:
        buffer = io.StringIO()

        print("generated SSA IR", file=buffer)

        if self.debug:
            print(self.make_ssa_instructions_log(ir), file=buffer)

        return buffer.getvalue()

    def make_bytecode_instructions_log(self, bytecode: list[Instruction]) -> str:
        buffer = io.StringIO()

        for instruction in bytecode:
            print(self.instruction_renderer.render(instruction), file=buffer)

        return buffer.getvalue().removesuffix("\n")

    def make_bytecode_generation_log(self, bytecode: list[Instruction]) -> str:
        buffer = io.StringIO()

        print(f"generated {len(bytecode)} instructions", file=buffer)

        if self.debug:
            print(self.make_bytecode_instructions_log(bytecode), file=buffer)

        return buffer.getvalue()

    def tokenize(self) -> None:
        tokens = Tokenizer(self.resources.file).run()
        self.logger.info("tokenized source")

        self.resources.tokens = tokens

    def parse(self) -> None:
        parse_tree = Parser(self.resources.tokens, self.logger).run()
        self.logger.info("parsed source")

        if self.debug:
            self.logger.debug(self.make_parse_tree_log(parse_tree))

        self.resources.parse_tree = parse_tree

    def generate_ssa_ir(self) -> None:
        ir = self.ir_generator.generate(self.resources.parse_tree)
        self.logger.info(self.make_ssa_ir_generation_log(ir))

        self.resources.ir = ir

    def generate_bytecode(self) -> None:
        bytecode = self.bytecode_generator.generate(self.resources.ir)
        self.logger.info(self.make_bytecode_generation_log(bytecode))

        if self.debug:
            bytecode.append(DumpMemory(0))
            self.logger.info("injected memory dump instruction")

        self.resources.bytecode = bytecode

    def compile(self) -> int:
        self.logger.info(f"starting compilation of {self.get_file_name()!r}")

        time_start = time.perf_counter()

        self.tokenize()
        self.parse()

        self.resources.file.close()
        self.logger.note("done with the file - closed")

        is_parse_tree_sane = self.sanity_checker.is_sane(self.resources.parse_tree)
        self.logger.info("checked parse tree sanity")

        if not is_parse_tree_sane:
            self.logger.info("found invalid nodes!")

            for node in self.sanity_checker.invalid_nodes:
                self.logger.error(node.message)

            self.logger.error("errors occurred - aborting")

            return 1

        self.logger.success("parse tree seems sane")

        self.generate_ssa_ir()
        self.generate_bytecode()

        time_end = time.perf_counter()

        if self.debug:
            self.logger.debug(f"compilation time: {time_end - time_start:.4f}s")

        return 0
