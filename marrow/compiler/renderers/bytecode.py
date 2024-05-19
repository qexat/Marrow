from __future__ import annotations

import typing

from marrow.compiler.backend.macroop import MacroOpVisitor

if typing.TYPE_CHECKING:
    from marrow.compiler.backend.macroop import Add
    from marrow.compiler.backend.macroop import Div
    from marrow.compiler.backend.macroop import DumpMemory
    from marrow.compiler.backend.macroop import Load
    from marrow.compiler.backend.macroop import MacroOp
    from marrow.compiler.backend.macroop import Mod
    from marrow.compiler.backend.macroop import Mul
    from marrow.compiler.backend.macroop import Neg
    from marrow.compiler.backend.macroop import Pos
    from marrow.compiler.backend.macroop import Store
    from marrow.compiler.backend.macroop import StoreImmediate
    from marrow.compiler.backend.macroop import Sub


class BytecodeRenderer(MacroOpVisitor[str]):
    def visit_add(self, op: Add) -> str:
        return f"\x1b[1m{'ADD':<16}\x1b[22m {op.destination:>#8x} {op.left:>#8x} {op.right:>#8x}"

    def visit_div(self, op: Div) -> str:
        return f"\x1b[1m{'DIV':<16}\x1b[22m {op.destination:>#8x} {op.left:>#8x} {op.right:>#8x}"

    def visit_dump_memory(self, op: DumpMemory) -> str:
        return f"\x1b[1m{'DUMP_MEMORY':<16}\x1b[22m {op.section_id:>#8x}"

    def visit_load(self, op: Load) -> str:
        return f"\x1b[1m{'LOAD':<16}\x1b[22m {op.destination:>#8x} {op.source:>#8x}"

    def visit_mod(self, op: Mod) -> str:
        return f"\x1b[1m{'MOD':<16}\x1b[22m {op.destination:>#8x} {op.left:>#8x} {op.right:>#8x}"

    def visit_mul(self, op: Mul) -> str:
        return f"\x1b[1m{'MUL':<16}\x1b[22m {op.destination:>#8x} {op.left:>#8x} {op.right:>#8x}"

    def visit_neg(self, op: Neg) -> str:
        return f"\x1b[1m{'NEG':<16}\x1b[22m {op.destination:>#8x} {op.source:>#8x}"

    def visit_pos(self, op: Pos) -> str:
        return f"\x1b[1m{'POS':<16}\x1b[22m {op.destination:>#8x} {op.source:>#8x}"

    def visit_store(self, op: Store) -> str:
        return f"\x1b[1m{'STORE':<16}\x1b[22m {op.destination:>#8x} {op.source:>#8x}"

    def visit_store_immediate(self, op: StoreImmediate) -> str:
        return f"\x1b[1m{'STOREI':<16}\x1b[22m {op.destination:>#8x} {op.immediate:>8}"

    def visit_sub(self, op: Sub) -> str:
        return f"\x1b[1m{'SUB':<16}\x1b[22m {op.destination:>#8x} {op.left:>#8x} {op.right:>#8x}"

    def render(self, op: MacroOp) -> str:
        return op.accept(self)
