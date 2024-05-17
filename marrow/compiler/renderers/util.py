from marrow.compiler.types import MemoryLocation


def render_memory_location(location: MemoryLocation) -> str:
    return f"mem{location}"
