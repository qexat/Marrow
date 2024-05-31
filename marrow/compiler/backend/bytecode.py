# pyright: reportImportCycles = false

from __future__ import annotations

import collections.abc
import typing

import attrs

if typing.TYPE_CHECKING:
    from marrow.compiler.common import MacroOp
    from marrow.compiler.resources import CompilerResources
    from marrow.types import MemoryAddress


@attrs.frozen
class Bytecode:
    file_name: str
    entry_point: MemoryAddress
    instructions: collections.abc.Iterable[MacroOp]

    @classmethod
    def from_resources(cls, resources: CompilerResources) -> typing.Self:
        return cls(
            resources.file_name,
            0,  # FIXME: the entry point address is hardcoded to 0 for now
            resources.macro_ops,
        )

    def __iter__(self) -> collections.abc.Generator[MacroOp, None, None]:
        yield from self.instructions
