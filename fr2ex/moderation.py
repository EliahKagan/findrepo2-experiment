"""
Checking OpenAI moderation endpoint results for repository names.

This project uses an OpenAI service (embeddings). But it does not involve
generating any content with OpenAI services. So checking the moderation
endpoint shouldn't be needed for compliance with the OpenAI content policy.

It may still be interesting. One use is to point out to the user that the
repository name they're interested in may inadvertently have unintended
interpretations. For example, a UI element that points out that a repo name is
a poor choice because it has whitespace, control characters, or other confusing
characters, could also point out if it seems to be not safe for work, or not
safe for life.

Note that, per https://beta.openai.com/docs/guides/moderation/overview:

    The moderation endpoint is free to use when monitoring the inputs and
    outputs of OpenAI APIs. We currently do not support monitoring of
    third-party traffic.

We are sending repository names as input to the text-embedding-ada-002, so this
should be fine. But it is important to keep in mind:

 1. Except in limited manual-testing scenarios, if we cache a repository name's
    embedding, and its moderation scores are also computed (including before),
    then we should also cache the moderation endpoint's output, so we don't end
    up sending significantly more requests to the moderation API than to the
    embeddings API.

 2. If we do an experiment that does not involve using any OpenAI models, for
    example if we compute embeddings with a non-OpenAI model without also
    computing them with an OpenAI model, then that experiment MUST NOT send the
    repository names (nor other data) to the OpenAI moderation endpoint.
"""

__all__ = ['Categories', 'CategoryScores', 'Result']

import contextlib
import json
import logging
from typing import Any, TypedDict

import blake3
import msgpack
import openai

from fr2ex import _apiutil


Categories = TypedDict('Categories', {
    'hate': bool,
    'hate/threatening': bool,
    'self-harm': bool,
    'sexual': bool,
    'sexual/minors': bool,
    'violence': bool,
    'violence/graphic': bool,
})
"""Each moderation category and whether or not it was flagged."""


CategoryScores = TypedDict('CategoryScores', {
    'hate': float,
    'hate/threatening': float,
    'self-harm': float,
    'sexual': float,
    'sexual/minors': float,
    'violence': float,
    'violence/graphic': float,
})
"""Each moderation category and the score for that category."""


class Result(TypedDict):
    """Result data, for a single text, from the OpenAI moderation endpoint."""

    categories: Categories
    """Each category and whether this moderation result shows it as flagged."""

    category_scores: CategoryScores
    """Each category's score as returned in this moderation result."""

    flagged: bool
    """Whether one or more categories are flagged in this moderation result."""


def get_moderation(texts: list[str]) -> list[Result]:
    """Load or query the API for a list of moderation results for all texts."""
    hexdigest = blake3.blake3(json.dumps(texts).encode()).hexdigest(length=16)
    filename = f'moderation-{hexdigest}.msgpack'

    with contextlib.suppress(FileNotFoundError):
        with open(filename, 'rb') as file:
            logging.info('Reading cached moderation results.')
            return msgpack.unpack(file)

    _apiutil.prepare()
    logging.info('Querying OpenAI moderation endpoint.')

    response: Any = openai.Moderation.create(input=texts)
    results = response.results

    with open(filename, 'wb') as file:
        msgpack.pack(results, file)

    return results
