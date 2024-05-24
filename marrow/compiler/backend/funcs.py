import enum


class BinaryArithmeticFunc(enum.IntEnum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MOD = enum.auto()


class UnaryArithmeticFunc(enum.IntEnum):
    POS = enum.auto()
    NEG = enum.auto()
