from __future__ import annotations

import collections.abc
import io
import itertools
import time
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
    from marrow.logger import Logger
    from marrow.types import RegisterIndex


class Machine(InstructionVisitor[None]):
    MEMORY_SIZE = 0x10000
    SECTION_SIZE = 0x100

    def __init__(self, logger: Logger) -> None:
        self.registers: list[int | float] = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]
        self.memory: list[int | float] = [0 for _ in range(self.MEMORY_SIZE)]

        self.register_tracking: set[RegisterIndex] = set()

        self.logger = logger

    def visit_load(self, instruction: Load) -> None:
        if instruction.destination != 0:
            self.registers[instruction.destination] = self.memory[instruction.source]
            self.register_tracking.add(instruction.destination)

    def visit_store(self, instruction: Store) -> None:
        self.memory[instruction.destination] = self.registers[instruction.source]
        self.register_tracking.add(instruction.source)

    def visit_store_immediate(self, instruction: StoreImmediate) -> None:
        self.memory[instruction.destination] = instruction.immediate

    def visit_add(self, instruction: Add) -> None:
        self.registers[instruction.destination] = (
            self.registers[instruction.left] + self.registers[instruction.right]
        )
        self.register_tracking.add(instruction.destination)
        self.register_tracking.add(instruction.left)
        self.register_tracking.add(instruction.right)

    def visit_sub(self, instruction: Sub) -> None:
        self.registers[instruction.destination] = (
            self.registers[instruction.left] - self.registers[instruction.right]
        )
        self.register_tracking.add(instruction.destination)
        self.register_tracking.add(instruction.left)
        self.register_tracking.add(instruction.right)

    def visit_mul(self, instruction: Mul) -> None:
        self.registers[instruction.destination] = (
            self.registers[instruction.left] * self.registers[instruction.right]
        )
        self.register_tracking.add(instruction.destination)
        self.register_tracking.add(instruction.left)
        self.register_tracking.add(instruction.right)

    def visit_div(self, instruction: Div) -> None:
        left = self.registers[instruction.left]
        right = self.registers[instruction.right]

        self.registers[instruction.destination] = (
            left // right
            if isinstance(left, int) and isinstance(right, int)
            else left / right
        )

        self.register_tracking.add(instruction.destination)
        self.register_tracking.add(instruction.left)
        self.register_tracking.add(instruction.right)

    def visit_mod(self, instruction: Mod) -> None:
        self.registers[instruction.destination] = (
            self.registers[instruction.left] % self.registers[instruction.right]
        )

        self.register_tracking.add(instruction.destination)
        self.register_tracking.add(instruction.left)
        self.register_tracking.add(instruction.right)

    def visit_pos(self, instruction: Pos) -> None:
        self.registers[instruction.destination] = +self.registers[instruction.source]

        self.register_tracking.add(instruction.destination)
        self.register_tracking.add(instruction.source)

    def visit_neg(self, instruction: Neg) -> None:
        self.registers[instruction.destination] = -self.registers[instruction.source]

        self.register_tracking.add(instruction.destination)
        self.register_tracking.add(instruction.source)

    def visit_dump_memory(self, instruction: DumpMemory) -> None:
        self.logger.debug(self._generate_dump_memory_log(instruction.section_id))

    def _to_hex_representation(self, value: int | float) -> str:
        base_repr = f"{int(value):02x}"

        if value == 0:
            return f"\x1b[2m{base_repr}\x1b[22m"

        return base_repr

    def _generate_dump_memory_log(self, section_id: int) -> str:
        buffer = io.StringIO()
        start = section_id * self.SECTION_SIZE
        section = self.memory[start : start + self.SECTION_SIZE]

        print(f"memory dump (section {section_id:#x})", file=buffer)

        for row in itertools.batched(section, 16):
            print(*map(self._to_hex_representation, row), file=buffer)

        return buffer.getvalue()

    def visit_instruction(self, instruction: Instruction) -> None:
        instruction.accept(self)

    def execute(
        self,
        instructions: collections.abc.Iterable[Instruction],
        *,
        debug: bool = False,
    ) -> None:
        time_start = time.perf_counter()

        for instruction in instructions:
            self.visit_instruction(instruction)

        time_end = time.perf_counter()

        if debug:
            self.logger.debug(f"execution time: {time_end - time_start:.4f}s")
            self.logger.debug(
                f"registers used: {', '.join(map(hex, self.register_tracking))}",
            )
