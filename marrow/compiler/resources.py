from __future__ import annotations

import collections.abc
import typing

import attrs

from marrow.compiler.frontend.ast.expr import BlockExpr

if typing.TYPE_CHECKING:
    from marrow.compiler.common import Expr
    from marrow.compiler.common import Instruction
    from marrow.compiler.common import IRInstruction
    from marrow.compiler.common import Token


@attrs.define
class CompilerResources:
    file: typing.TextIO
    tokens: collections.abc.Iterator[Token] = attrs.field(factory=lambda: iter(()))
    parse_tree: Expr = attrs.field(factory=lambda: BlockExpr([]))
    ir: list[IRInstruction] = attrs.field(factory=list)
    bytecode: list[Instruction] = attrs.field(factory=list)
