from __future__ import annotations

import typing

from marrow.compiler.backend.macro.ops import BinaryArithmetic
from marrow.compiler.backend.macro.ops import MacroOpVisitor
from marrow.compiler.backend.macro.ops import UnaryArithmetic

if typing.TYPE_CHECKING:
    from marrow.compiler.backend.macro.ops import DumpMemory
    from marrow.compiler.backend.macro.ops import Load
    from marrow.compiler.backend.macro.ops import Store
    from marrow.compiler.backend.macro.ops import StoreImmediate
    from marrow.compiler.common import MacroOp


class MacroOpRenderer(MacroOpVisitor[str]):
    def visit_binary_arithmetic(self, op: BinaryArithmetic) -> str:
        return f"\x1b[1m{op.func.name:<16}\x1b[22m {op.destination:>#16x} {op.left:>#16x} {op.right:>#16x}"

    def visit_dump_memory(self, op: DumpMemory) -> str:
        return f"\x1b[1m{'DUMP_MEMORY':<16}\x1b[22m {op.section_id:>#16x}"

    def visit_load(self, op: Load) -> str:
        return f"\x1b[1m{'LOAD':<16}\x1b[22m {op.destination:>#16x} {op.source:>#16x}"

    def visit_store(self, op: Store) -> str:
        return f"\x1b[1m{'STORE':<16}\x1b[22m {op.destination:>#16x} {op.source:>#16x}"

    def visit_store_immediate(self, op: StoreImmediate) -> str:
        immediate = int.from_bytes(op.immediate)

        return f"\x1b[1m{'STOREIMM':<16}\x1b[22m {op.destination:>#16x} {immediate:>16}"

    def visit_unary_arithmetic(self, op: UnaryArithmetic) -> str:
        return f"\x1b[1m{op.func.name:<16}\x1b[22m {op.destination:>#16x} {op.source:>#16x}"

    def render(self, op: MacroOp) -> str:
        return op.accept(self)
