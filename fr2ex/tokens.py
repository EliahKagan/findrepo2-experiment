# Copyright (c) 2023 Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
Counting and displaying cl100k_base tokens (used by text-embedding-ada-002).

This also computes pricing estimates for the text-embedding-ada-002 models.
"""

__all__ = [
    'DEFAULT_BASE_STYLING',
    'DEFAULT_STYLING_CYCLE',
    'PriceRetrievalError',
    'Rate',
    'count',
    'find_embedding_model_prices',
    'report_cost',
    'show',
]

import datetime
from decimal import Decimal
import functools
import io
import re
import textwrap
from typing import Iterable, Iterator, Optional, Sequence

import attrs
import bs4
import colorama
import pandas
import requests
import tiktoken

DEFAULT_BASE_STYLING = colorama.Style.BRIGHT + colorama.Fore.BLACK
"""Default for styling that stays the same for all tokens being displayed."""

# FIXME: Pick a more accessible default.
DEFAULT_STYLING_CYCLE = (
    colorama.Back.LIGHTGREEN_EX,
    colorama.Back.LIGHTMAGENTA_EX,
)
"""Default for the two or more stylings that vary across consecutive tokens."""

_END_STYLED_LINE = colorama.Style.RESET_ALL + '\n'
"""String to reset styling, followed by a newline. This should not change."""

_RATE_PATTERN = re.compile(r'\A\s*\$([\d.]+)\s*/\s*1K\s+tokens\s*\Z')
"""Regex to parse rates. Currently all rates are given per 1K tokens."""

_RATE_PATTERN_DENOMINATOR = 1000
"""The denominator that _RATE_PATTERN currently works with."""

_REQUEST_TIMEOUT = datetime.timedelta(seconds=30)

_find_model_heading = functools.partial(
    bs4.Tag.find_all,
    name='h3',
    attrs={'class': 'f-heading-3'},
)
"""Select model category headings in a given element. Use like find_all."""

_encoding = tiktoken.get_encoding('cl100k_base')
"""cl100k_base encoder/decoder."""

_encode_many = functools.partial(_encoding.encode_batch, num_threads=1)
"""Separately encode all texts in a list as lists of cl100k_base tokens."""

_decode_one = functools.partial(_encoding.decode, errors='strict')
"""Decode one list of cl100k_base tokens as text. Use strict error handling."""


class PriceRetrievalError(Exception):
    """Model pricing data couldn't be obtained."""


@attrs.frozen
class Rate:
    """A pricing rate."""

    numerator: Decimal
    """The stated price in US dollars (per some number of tokens)."""

    denominator: int
    """The number of tokens the stated price is for."""

    def __str__(self) -> str:
        """Representation of this rate suitable for user interfaces."""
        return f'${self.numerator} per {self.denominator} tokens'

    @property
    def value(self) -> Decimal:
        """The value of this rate as a Decimal instance."""
        return self.numerator / self.denominator


def _parse_rate(text: str) -> Rate:
    """Parse pricing from informal text, returning a Rate."""
    match = _RATE_PATTERN.fullmatch(text)
    if match is None:
        raise PriceRetrievalError(f"can't parse rate: {text.strip()}")
    return Rate(Decimal(match[1]), _RATE_PATTERN_DENOMINATOR)


@functools.cache
def _get_pricing_page() -> str:
    """Retrieve the pricing page from the OpenAI website."""
    response = requests.get(
        url='https://openai.com/pricing/',
        timeout=_REQUEST_TIMEOUT.total_seconds(),
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def _need(condition: bool) -> None:
    """Raise PriceRetrievalError if the condition is not satisfied."""
    if not condition:
        raise PriceRetrievalError("can't find embedding model prices on page")


def find_embedding_model_prices(
    *, displayed_only: bool = True,
) -> dict[str, Rate]:
    """Retrieve the prices of embedding models."""
    doc = bs4.BeautifulSoup(_get_pricing_page(), features='lxml')

    headings = _find_model_heading(doc, string='Embedding models')
    _need(len(headings) == 1)
    doc_row = headings[0].parent.parent.parent.parent
    _need(len(_find_model_heading(doc_row)) == 1)

    doc_row_html = io.StringIO(str(doc_row))
    frames = pandas.read_html(doc_row_html, displayed_only=displayed_only)
    data_header, *data_rows = (row for df in frames for row in df.values)
    _need((data_header == ('Model', 'Usage')).all())
    return {name: _parse_rate(text) for name, text in data_rows}


def count(texts: list[str]) -> int:
    """Count how many total cl100k_base tokens are in all the given texts."""
    return sum(len(tokens) for tokens in _encode_many(texts))


def report_cost(texts: list[str]) -> None:
    """Report a cost estimate for calling text-embedding-ada-002 on texts."""
    rate = find_embedding_model_prices()['ada v2']
    token_count = count(texts)
    total_cost = token_count * rate.value

    message = (
        f'It looks like the rate is {rate}. If so, the cost to process '
        f'{token_count} tokens is about ${total_cost} '
        f'(that is, {total_cost * 100} cents).'
    )

    for line in textwrap.wrap(message):
        print(line)


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


def _style_one(tokens: Iterable[int],
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
