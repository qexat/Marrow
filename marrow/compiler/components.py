"""
Components of the compiler.
"""

from marrow.compiler.backend.macro.generator import MacroOpGenerator
from marrow.compiler.frontend.parser.parser import Parser
from marrow.compiler.frontend.ptsc import ParseTreeSanityChecker
from marrow.compiler.frontend.tokenizer import Tokenizer
from marrow.compiler.middleend.SSAIR.generator import IRGenerator

__all__ = [
    "MacroOpGenerator",
    "IRGenerator",
    "Parser",
    "ParseTreeSanityChecker",
    "Tokenizer",
]
