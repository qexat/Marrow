import io
import typing

import attrs

from marrow.compiler.common import Token
from marrow.compiler.common import TokenType
from marrow.compiler.frontend.ast import expr

type NodeAttributeType = TokenType | Token | expr.Expr | list[expr.Expr] | str


@attrs.frozen
class ParseTreeRenderer(expr.ExprVisitor[str]):
    indent_size: int = 4

    @typing.overload
    def render_node_attribute(self, name: str, expression: expr.Expr, /) -> str: ...
    @typing.overload
    def render_node_attribute(
        self,
        name: str,
        expression_list: list[expr.Expr],
        /,
    ) -> str: ...
    @typing.overload
    def render_node_attribute(self, name: str, string: str, /) -> str: ...
    @typing.overload
    def render_node_attribute(self, name: str, token: Token, /) -> str: ...
    @typing.overload
    def render_node_attribute(self, name: str, token_type: TokenType, /) -> str: ...

    def render_node_attribute(self, name: str, value: NodeAttributeType, /) -> str:
        buffer = io.StringIO()

        match value:
            case expr.ExprBase():
                rendering = self._render_expr_attribute(name, value)
            case list():
                rendering = self._render_expr_list_attribute(name, value)
            case str():
                rendering = self._render_string_attribute(name, value)
            case Token():
                rendering = self._render_token_attribute(name, value)
            case TokenType():
                rendering = self._render_token_type_attribute(name, value)

        buffer.write(rendering)
        buffer.write(",\n")

        return buffer.getvalue()

    def _render_attribute_prelude(self, name: str) -> str:
        return " " * self.indent_size + f"{name}\x1b[38;2;233;198;175m=\x1b[39m"

    def _render_attribute_node(self, expression: expr.Expr, indents: int = 0) -> str:
        buffer = io.StringIO()

        expr_repr = expression.accept(self)
        first, *lines = expr_repr.splitlines()

        print(" " * self.indent_size * indents + f"{first}", file=buffer)

        for index, line in enumerate(lines):
            if index > 0:
                buffer.write("\n")
            buffer.write(" " * self.indent_size * (indents + 1) + line)

        return buffer.getvalue()

    def _render_expr_attribute(self, name: str, expression: expr.Expr) -> str:
        buffer = io.StringIO()

        buffer.write(self._render_attribute_prelude(name))
        buffer.write(self._render_attribute_node(expression))

        return buffer.getvalue()

    def _render_expr_list_attribute(
        self,
        name: str,
        expression_list: list[expr.Expr],
    ) -> str:
        buffer = io.StringIO()

        buffer.write(self._render_attribute_prelude(name) + "[")

        if expression_list:
            buffer.write("\n")

        for subexpr in expression_list:
            buffer.write(self._render_attribute_node(subexpr, indents=2))
            buffer.write(",\n")

        if expression_list:
            buffer.write(" " * self.indent_size)

        buffer.write("]")

        return buffer.getvalue()

    def _render_string_attribute(self, name: str, string: str) -> str:
        return self._render_attribute_prelude(name) + repr(string)

    def _render_token_attribute(self, name: str, token: Token) -> str:
        buffer = io.StringIO()

        buffer.write(self._render_attribute_prelude(name))
        buffer.write(f"<Token \x1b[92m{token.lexeme!r}\x1b[39m {token.span}>")

        return buffer.getvalue()

    def _render_token_type_attribute(self, name: str, token_type: TokenType) -> str:
        buffer = io.StringIO()

        buffer.write(self._render_attribute_prelude(name))
        buffer.write(f"\x1b[96m{token_type.name}\x1b[39m")

        return buffer.getvalue()

    def visit_expr(self, expression: expr.Expr) -> str:
        buffer = io.StringIO()

        print(f"\x1b[93m{expression.__class__.__name__}\x1b[39m(", file=buffer)

        for key, value in expression.__dict__.items():
            buffer.write(self.render_node_attribute(key, value))

        print(")", file=buffer)

        return buffer.getvalue()

    def visit_binary_expr(self, expression: expr.BinaryExpr) -> str:
        return self.visit_expr(expression)

    def visit_block_expr(self, expression: expr.BlockExpr) -> str:
        return self.visit_expr(expression)

    def visit_grouping_expr(self, expression: expr.GroupingExpr) -> str:
        return self.visit_expr(expression)

    def visit_invalid_expr(self, expression: expr.InvalidExpr) -> str:
        return self.visit_expr(expression)

    def visit_literal_scalar_expr(self, expression: expr.LiteralScalarExpr) -> str:
        return self.visit_expr(expression)

    def visit_mod_expr(self, expression: expr.ModExpr) -> str:
        return self.visit_expr(expression)

    def visit_unary_expr(self, expression: expr.UnaryExpr) -> str:
        return self.visit_expr(expression)

    def render(self, expression: expr.Expr) -> str:
        return expression.accept(self)
