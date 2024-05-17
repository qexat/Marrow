from marrow.compiler.frontend.ast import expr
from marrow.compiler.types import MemoryLocation

from .instruction import IRInstruction
from .rvalue import AtomicRValue
from .rvalue import BinaryRValue
from .rvalue import UnaryRValue


class IRGenerator(expr.ExprVisitor[None]):
    def __init__(self) -> None:
        self.instructions: list[IRInstruction] = []
        self.expr_registers: dict[expr.Expr, MemoryLocation] = {}
        self.location = 0

    def allocate_location(self, expr: expr.Expr) -> MemoryLocation:
        location = self.location

        self.expr_registers[expr] = location
        self.location += 1

        return location

    def visit_binary_expr(self, expression: expr.BinaryExpr) -> None:
        expression.left.accept(self)
        expression.right.accept(self)

        left = self.expr_registers[expression.left]
        right = self.expr_registers[expression.right]
        destination = self.allocate_location(expression)

        rvalue = BinaryRValue(expression.operator, left, right)
        instruction = IRInstruction(destination, rvalue)

        self.instructions.append(instruction)

    def visit_block_expr(self, expression: expr.BlockExpr) -> None:
        for subexpr in expression.expr_list:
            subexpr.accept(self)

    def visit_grouping_expr(self, expression: expr.GroupingExpr) -> None:
        expression.grouped.accept(self)

    def visit_invalid_expr(self, expression: expr.InvalidExpr) -> None:
        raise TypeError("found invalid expression while generating SSA IR")

    def visit_literal_scalar_expr(self, expression: expr.LiteralScalarExpr) -> None:
        location = self.allocate_location(expression)
        instruction = IRInstruction(location, AtomicRValue(expression.token))

        self.instructions.append(instruction)

    def visit_mod_expr(self, expression: expr.ModExpr) -> None:
        expression.expr.accept(self)

    def visit_unary_expr(self, expression: expr.UnaryExpr) -> None:
        expression.operand.accept(self)

        right = self.expr_registers[expression.operand]
        destination = self.allocate_location(expression)

        rvalue = UnaryRValue(expression.operator, right)
        instruction = IRInstruction(destination, rvalue)

        self.instructions.append(instruction)

    def generate(self, expr: expr.Expr) -> list[IRInstruction]:
        expr.accept(self)

        return self.instructions
