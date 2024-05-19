from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from marrow.types import MemoryAddress


def render_memory_location(location: MemoryAddress) -> str:
    return f"mem{location}"
