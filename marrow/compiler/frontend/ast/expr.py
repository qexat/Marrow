from __future__ import annotations

import abc
import enum
import typing

import attrs

from ..token import Token
from ..token_type import BinaryOpTokenType
from ..token_type import LiteralTokenType
from ..token_type import UnaryOpTokenType


class LiteralScalarType(enum.Enum):
    INTEGER = enum.auto()
    FLOAT = enum.auto()


class ExprVisitor[R_co](typing.Protocol):
    """
    Interface determining the methods required to traverse the AST.

    An `ExprVisitor` instance can either implement them independently, or
    inherit from this class which will then act as an abstract class.
    """

    def visit_invalid_expr(self, expression: InvalidExpr) -> R_co: ...

    def visit_literal_scalar_expr(self, expression: LiteralScalarExpr) -> R_co: ...

    def visit_block_expr(self, expression: BlockExpr) -> R_co: ...
    def visit_grouping_expr(self, expression: GroupingExpr) -> R_co: ...
    def visit_mod_expr(self, expression: ModExpr) -> R_co: ...

    def visit_unary_expr(self, expression: UnaryExpr) -> R_co: ...
    def visit_binary_expr(self, expression: BinaryExpr) -> R_co: ...


class ExprBase(abc.ABC):
    """
    Base class from which every AST node inherits from.
    """

    @abc.abstractmethod
    def accept[R](self, visitor: ExprVisitor[R]) -> R:
        """
        Entry point used by the visitor to traverse the AST.

        Parameters
        ----------
        visitor : ExprVisitor[R]
        """


@attrs.frozen(slots=False)
class BinaryExpr(ExprBase):
    """
    Node representing a binary expression.

    Attributes
    ----------
    operator : BinaryOpTokenType
        The token type of the binary operator.
    left : Expr
        The expression on the left handside of the operator.
    right : Expr
        The expression on the right handside of the operator.
    """

    operator: BinaryOpTokenType
    left: Expr
    right: Expr

    def accept[R](self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_binary_expr(self)


@attrs.frozen(slots=False)
class BlockExpr(ExprBase):
    """
    Node representing a block expression.

    Attributes
    ----------
    expr_list : list[Expr]
        The list of expressions contained in the block.
    """

    expr_list: list[Expr]

    def accept[R](self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_block_expr(self)


@attrs.frozen(slots=False)
class GroupingExpr(ExprBase):
    """
    Node representing an expression surrounded by parentheses.

    Attributes
    ----------
    grouped : Expr
        The parenthesized expression.
    """

    grouped: Expr

    def accept[R](self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_grouping_expr(self)


@attrs.frozen(slots=False)
class InvalidExpr(ExprBase):
    """
    Node representing an generic, invalid expression.

    Attributes
    ----------
    message : str
        The parsing error message.
    token : Token
        The token that resulted in this invalid node.
    subexprs : list[Expr]
        The sub-nodes below this one.
    """

    message: str
    token: Token
    subexprs: list[Expr] = []

    def accept[R](self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_invalid_expr(self)


@attrs.frozen(slots=False)
class LiteralScalarExpr(ExprBase):
    """
    Node representing a scalar literal.

    Attributes
    ----------
    token : Token
        The token that corresponds to the literal.
    type : LiteralScalarType
        The literal type.
    """

    token: Token
    type: LiteralTokenType

    def accept[R](self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_literal_scalar_expr(self)


@attrs.frozen(slots=False)
class ModExpr(ExprBase):
    """
    Node representing a module expression.

    Attributes
    ----------
    expr : Expr
        The expression of the module.
    """

    expr: Expr

    def accept[R](self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_mod_expr(self)


@attrs.frozen(slots=False)
class UnaryExpr(ExprBase):
    """
    Node representing a unary expression.

    Attributes
    ----------
    operator : UnaryOpTokenType
        The token type of the unary operator.
    expr : Expr
        The expression affected by this operator.
    """

    operator: UnaryOpTokenType
    operand: Expr

    def accept[R](self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_unary_expr(self)


type LiteralExpr = LiteralScalarExpr
"""Node representing a literal."""
type ScopeExpr = BlockExpr | ModExpr
"""Node representing a block or scoping expression."""
type AtomicExpr = GroupingExpr | LiteralExpr | ScopeExpr
"""Node representing an atom."""
type ValidExpr = AtomicExpr | BinaryExpr | UnaryExpr
"""Node representing a valid expression."""
type Expr = InvalidExpr | ValidExpr
"""Node representing an expression, with support for exhaustiveness checking."""
