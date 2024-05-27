import typing

import attrs

from marrow.compiler.backend.macro.generator import MacroOpGenerator
from marrow.compiler.frontend.ptsc import ParseTreeSanityChecker
from marrow.compiler.middleend.SSAIR.generator import IRGenerator
from marrow.compiler.renderers.macroop import MacroOpRenderer
from marrow.compiler.renderers.parse_tree import ParseTreeRenderer
from marrow.compiler.renderers.rvalue import RValueRenderer
from marrow.endec import EncoderDecoder
from marrow.logger import Logger
from marrow.runtime.alu.alu import ArithmeticLogicUnit


@attrs.frozen
class GlobalTooling:
    endec: EncoderDecoder
    logger: Logger

    @classmethod
    def new(cls, *, verbose: bool) -> typing.Self:
        return cls(EncoderDecoder(), Logger(verbose=verbose))


@attrs.frozen
class CompilerTooling(GlobalTooling):
    sanity_checker: ParseTreeSanityChecker
    parse_tree_renderer: ParseTreeRenderer
    ir_generator: IRGenerator
    rvalue_renderer: RValueRenderer
    macro_op_generator: MacroOpGenerator
    macro_op_renderer: MacroOpRenderer

    @classmethod
    def from_global(cls, tooling: GlobalTooling) -> typing.Self:
        return cls(
            tooling.endec,
            tooling.logger,
            ParseTreeSanityChecker(),
            ParseTreeRenderer(),
            IRGenerator(),
            RValueRenderer(),
            MacroOpGenerator(tooling),
            MacroOpRenderer(),
        )


@attrs.frozen
class RuntimeTooling(GlobalTooling):
    alu: ArithmeticLogicUnit

    @classmethod
    def from_global(cls, tooling: GlobalTooling) -> typing.Self:
        return cls(tooling.endec, tooling.logger, ArithmeticLogicUnit(tooling))
