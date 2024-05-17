from __future__ import annotations

import typing

from marrow.compiler.backend.instruction import InstructionVisitor

if typing.TYPE_CHECKING:
    from marrow.compiler.backend.instruction import Add
    from marrow.compiler.backend.instruction import Div
    from marrow.compiler.backend.instruction import DumpMemory
    from marrow.compiler.backend.instruction import Instruction
    from marrow.compiler.backend.instruction import Load
    from marrow.compiler.backend.instruction import Mod
    from marrow.compiler.backend.instruction import Mul
    from marrow.compiler.backend.instruction import Neg
    from marrow.compiler.backend.instruction import Pos
    from marrow.compiler.backend.instruction import Store
    from marrow.compiler.backend.instruction import StoreImmediate
    from marrow.compiler.backend.instruction import Sub


class BytecodeRenderer(InstructionVisitor[str]):
    def visit_add(self, instruction: Add) -> str:
        return f"\x1b[1m{'ADD':<16}\x1b[22m {instruction.destination:>#8x} {instruction.left:>#8x} {instruction.right:>#8x}"

    def visit_div(self, instruction: Div) -> str:
        return f"\x1b[1m{'DIV':<16}\x1b[22m {instruction.destination:>#8x} {instruction.left:>#8x} {instruction.right:>#8x}"

    def visit_dump_memory(self, instruction: DumpMemory) -> str:
        return f"\x1b[1m{'DUMP_MEMORY':<16}\x1b[22m {instruction.section_id:>#8x}"

    def visit_load(self, instruction: Load) -> str:
        return f"\x1b[1m{'LOAD':<16}\x1b[22m {instruction.destination:>#8x} {instruction.source:>#8x}"

    def visit_mod(self, instruction: Mod) -> str:
        return f"\x1b[1m{'MOD':<16}\x1b[22m {instruction.destination:>#8x} {instruction.left:>#8x} {instruction.right:>#8x}"

    def visit_mul(self, instruction: Mul) -> str:
        return f"\x1b[1m{'MUL':<16}\x1b[22m {instruction.destination:>#8x} {instruction.left:>#8x} {instruction.right:>#8x}"

    def visit_neg(self, instruction: Neg) -> str:
        return f"\x1b[1m{'NEG':<16}\x1b[22m {instruction.destination:>#8x} {instruction.source:>#8x}"

    def visit_pos(self, instruction: Pos) -> str:
        return f"\x1b[1m{'POS':<16}\x1b[22m {instruction.destination:>#8x} {instruction.source:>#8x}"

    def visit_store(self, instruction: Store) -> str:
        return f"\x1b[1m{'STORE':<16}\x1b[22m {instruction.destination:>#8x} {instruction.source:>#8x}"

    def visit_store_immediate(self, instruction: StoreImmediate) -> str:
        return f"\x1b[1m{'STOREI':<16}\x1b[22m {instruction.destination:>#8x} {instruction.immediate:>8}"

    def visit_sub(self, instruction: Sub) -> str:
        return f"\x1b[1m{'SUB':<16}\x1b[22m {instruction.destination:>#8x} {instruction.left:>#8x} {instruction.right:>#8x}"

    def render(self, instruction: Instruction) -> str:
        return instruction.accept(self)
