"""
Counting and displaying cl100k_base tokens (used by text-embedding-ada-002).
"""

__all__ = ['DEFAULT_BASE_STYLING', 'DEFAULT_STYLING_CYCLE', 'count', 'show']

import functools
from typing import Iterable, Iterator, Optional, Sequence

import colorama
import tiktoken

DEFAULT_BASE_STYLING = colorama.Style.BRIGHT + colorama.Fore.BLACK
"""The styling that stays the same for all tokens being displayed."""

# TODO: If this code is being distributed, pick a more accessible default.
DEFAULT_STYLING_CYCLE = (
    colorama.Back.LIGHTGREEN_EX,
    colorama.Back.LIGHTMAGENTA_EX,
)
"""The stylings that vary across consecutive tokens. (Needs at least two.)"""

_END_STYLED_LINE = colorama.Style.RESET_ALL + '\n'
"""String to reset styling, followed by a newline. Do not change this."""

_encoding = tiktoken.get_encoding('cl100k_base')
"""cl100k_base encoder/decoder."""

_encode_many = functools.partial(_encoding.encode_batch, num_threads=1)
"""Separately encode all texts in a list as lists of cl100k_base tokens."""

_decode_one = functools.partial(_encoding.decode, errors='strict')
"""Decode one list of cl100k_base tokens as text. Use strict error handling."""


def count(texts: list[str]) -> int:
    """Count how many total cl100k_base tokens are in all the given texts."""
    return sum(len(tokens) for tokens in _encode_many(texts))


def show(texts: list[str], *,
         base_styling: Optional[str] = None,
         styling_cycle: Optional[Sequence[str]] = None) -> None:
    """Display texts, showing how they break down into cl100k_base tokens."""
    if base_styling is None:
        base_styling = DEFAULT_BASE_STYLING
    if styling_cycle is None:
        styling_cycle = DEFAULT_STYLING_CYCLE

    if len(styling_cycle) < 2:
        raise ValueError('styling cycle needs at least 2 elements')
    if len(set(styling_cycle)) != len(styling_cycle):
        raise ValueError('styling cycle elements must all be distinct')

    return _do_show(texts, base_styling, styling_cycle)


def _style_one(tokens: Iterable[str],
               base_styling: str,
               styling_cycle: Sequence[str]) -> Iterator[str]:
    """Style a single series of tokens, yielding each styled piece."""
    pieces = (_decode_one([token]) for token in tokens)

    for index, piece in enumerate(pieces):
        indexed_styling = styling_cycle[index % len(styling_cycle)]
        yield f'{base_styling}{indexed_styling}{piece}'


def _do_show(texts: list[str],
             base_styling: str,
             styling_cycle: Sequence[str]) -> None:
    """Like show. Doesn't validate arguments. Implementation detail of show."""
    for tokens in _encode_many(texts):
        styled_pieces = _style_one(tokens, base_styling, styling_cycle)
        print(*styled_pieces, sep='', end=_END_STYLED_LINE)
