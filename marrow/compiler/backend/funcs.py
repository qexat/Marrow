import enum


class BinaryArithFunc(enum.IntEnum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MOD = enum.auto()


class UnaryArithFunc(enum.IntEnum):
    POS = enum.auto()
    NEG = enum.auto()
