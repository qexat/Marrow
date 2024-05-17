from .ast import expr


class ParseTreeSanityChecker(expr.ExprVisitor[None]):
    def __init__(self) -> None:
        self.invalid_nodes: list[expr.InvalidExpr] = []

    def visit_binary_expr(self, expression: expr.BinaryExpr) -> None:
        expression.left.accept(self)
        expression.right.accept(self)

    def visit_block_expr(self, expression: expr.BlockExpr) -> None:
        for subexpr in expression.expr_list:
            subexpr.accept(self)

    def visit_grouping_expr(self, expression: expr.GroupingExpr) -> None:
        expression.grouped.accept(self)

    def visit_invalid_expr(self, expression: expr.InvalidExpr) -> None:
        self.invalid_nodes.append(expression)

    def visit_literal_scalar_expr(self, expression: expr.LiteralScalarExpr) -> None:
        pass

    def visit_mod_expr(self, expression: expr.ModExpr) -> None:
        expression.expr.accept(self)

    def visit_unary_expr(self, expression: expr.UnaryExpr) -> None:
        expression.operand.accept(self)

    def is_sane(self, parse_tree: expr.Expr) -> bool:
        """
        Parameters
        ----------
        parse_tree : Expr
            The parse tree to check.

        Returns
        -------
        bool
            Whether the parse tree is sane or not.
        """
        parse_tree.accept(self)

        return not self.invalid_nodes
