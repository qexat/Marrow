# pyright: reportUnusedCallResult = false

from __future__ import annotations

import io
import typing

from marrow.compiler.common import TokenType
from marrow.compiler.middleend.SSAIR import rvalue

from .util import render_memory_location

if typing.TYPE_CHECKING:
    from marrow.compiler.frontend.token_type import AtomTokenType


class RValueRenderer(rvalue.RValueVisitor[str]):
    def visit_atomic_rvalue(self, value: rvalue.AtomicRValue) -> str:
        lexeme = value.token.lexeme

        match typing.cast("AtomTokenType", value.token.type):
            case TokenType.INTEGER | TokenType.FLOAT:
                return f"\x1b[96m{lexeme}\x1b[39m"
            case _:
                return value.token.lexeme

    def visit_binary_rvalue(self, value: rvalue.BinaryRValue) -> str:
        buffer = io.StringIO()

        buffer.write(render_memory_location(value.left))
        buffer.write(" \x1b[38;2;233;198;175m")

        match value.kind:
            case TokenType.MINUS:
                buffer.write("-")
            case TokenType.PERCENT:
                buffer.write("%")
            case TokenType.PLUS:
                buffer.write("+")
            case TokenType.SLASH:
                buffer.write("/")
            case TokenType.STAR:
                buffer.write("*")

        buffer.write("\x1b[39m ")
        buffer.write(render_memory_location(value.right))

        return buffer.getvalue()

    def visit_unary_rvalue(self, value: rvalue.UnaryRValue) -> str:
        buffer = io.StringIO()
        buffer.write("\x1b[38;2;233;198;175m")

        match value.kind:
            case TokenType.MINUS:
                buffer.write("-")
            case TokenType.PLUS:
                buffer.write("+")

        buffer.write("\x1b[39m")
        buffer.write(render_memory_location(value.right))

        return buffer.getvalue()

    def render(self, value: rvalue.RValue) -> str:
        return value.accept(self)
