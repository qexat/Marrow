import enum


class Precedence(enum.IntEnum):
    """Table of precedence of the binary operators."""

    ADDITION = 1
    SUBTRACTION = 1
    MULTIPLICATION = 2
    DIVISION = 2
    REMAINDER = 2
