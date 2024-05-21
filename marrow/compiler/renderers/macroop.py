from __future__ import annotations

import typing

from marrow.compiler.backend.macro.ops import MacroOpVisitor

if typing.TYPE_CHECKING:
    from marrow.compiler.backend.macro.ops import Add
    from marrow.compiler.backend.macro.ops import Div
    from marrow.compiler.backend.macro.ops import DumpMemory
    from marrow.compiler.backend.macro.ops import Load
    from marrow.compiler.backend.macro.ops import MacroOp
    from marrow.compiler.backend.macro.ops import Mod
    from marrow.compiler.backend.macro.ops import Mul
    from marrow.compiler.backend.macro.ops import Neg
    from marrow.compiler.backend.macro.ops import Pos
    from marrow.compiler.backend.macro.ops import Store
    from marrow.compiler.backend.macro.ops import StoreImmediate
    from marrow.compiler.backend.macro.ops import Sub


class MacroOpRenderer(MacroOpVisitor[str]):
    def visit_add(self, op: Add) -> str:
        return f"\x1b[1m{'ADD':<16}\x1b[22m {op.destination:>#16x} {op.left:>#16x} {op.right:>#16x}"

    def visit_div(self, op: Div) -> str:
        return f"\x1b[1m{'DIV':<16}\x1b[22m {op.destination:>#16x} {op.left:>#16x} {op.right:>#16x}"

    def visit_dump_memory(self, op: DumpMemory) -> str:
        return f"\x1b[1m{'DUMP_MEMORY':<16}\x1b[22m {op.section_id:>#16x}"

    def visit_load(self, op: Load) -> str:
        return f"\x1b[1m{'LOAD':<16}\x1b[22m {op.destination:>#16x} {op.source:>#16x}"

    def visit_mod(self, op: Mod) -> str:
        return f"\x1b[1m{'MOD':<16}\x1b[22m {op.destination:>#16x} {op.left:>#16x} {op.right:>#16x}"

    def visit_mul(self, op: Mul) -> str:
        return f"\x1b[1m{'MUL':<16}\x1b[22m {op.destination:>#16x} {op.left:>#16x} {op.right:>#16x}"

    def visit_neg(self, op: Neg) -> str:
        return f"\x1b[1m{'NEG':<16}\x1b[22m {op.destination:>#16x} {op.source:>#16x}"

    def visit_pos(self, op: Pos) -> str:
        return f"\x1b[1m{'POS':<16}\x1b[22m {op.destination:>#16x} {op.source:>#16x}"

    def visit_store(self, op: Store) -> str:
        return f"\x1b[1m{'STORE':<16}\x1b[22m {op.destination:>#16x} {op.source:>#16x}"

    def visit_store_immediate(self, op: StoreImmediate) -> str:
        immediate = int.from_bytes(op.immediate)

        return f"\x1b[1m{'STOREI':<16}\x1b[22m {op.destination:>#16x} {immediate:>16}"

    def visit_sub(self, op: Sub) -> str:
        return f"\x1b[1m{'SUB':<16}\x1b[22m {op.destination:>#16x} {op.left:>#16x} {op.right:>#16x}"

    def render(self, op: MacroOp) -> str:
        return op.accept(self)
