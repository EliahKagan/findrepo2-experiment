"""
Computing text embeddings of repository names.

The text embeddings computed are computed with OpenAI's new (in December 2022)
model text-embedding-ada-002.
"""

import contextlib
import json
import logging
import msgpack
import msgpack_numpy

import blake3
import numpy as np
from numpy.typing import NDArray
import openai.embeddings_utils

from fr2ex import _apiutil

msgpack_numpy.patch()


def embed_many(texts: list[str]) -> NDArray[np.float32]:
    """Load or query the API for text-embedding-ada-002 for all texts."""
    hexdigest = blake3.blake3(json.dumps(texts).encode()).hexdigest(length=16)
    filename = f'embeddings-{hexdigest}.msgpack'

    with contextlib.suppress(FileNotFoundError):
        with open(filename, 'rb') as file:
            logging.info('Reading cached embeddings.')
            return msgpack.unpack(file)

    _apiutil.prepare()
    logging.info('Querying OpenAI embeddings endpoint.')

    embeddings = np.array(openai.embeddings_utils.get_embeddings(
        list_of_text=texts,
        engine='text-embedding-ada-002',
    ))

    with open(filename, 'wb') as file:
        msgpack.pack(embeddings, file)

    return embeddings
