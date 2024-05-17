from .atomexpr import AtomSubparser
from .nonprefixexpr import NonprefixSubparser
from .prefixexpr import PrefixSubparser

__all__ = [
    "AtomSubparser",
    "NonprefixSubparser",
    "PrefixSubparser",
    "Subparser",
]

type Subparser = AtomSubparser | NonprefixSubparser | PrefixSubparser
"""Specialized parser for a specific expression."""
