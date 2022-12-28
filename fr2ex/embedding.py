"""
Computing text embeddings of repository names.

The text embeddings computed are computed with OpenAI's new (in December 2022)
model text-embedding-ada-002.
"""

__all__ = ['embed_many']

import numpy as np
from numpy.typing import NDArray
import openai.embeddings_utils

from fr2ex import _task


@_task.api_task('embeddings')
def embed_many(texts: list[str]) -> NDArray[np.float32]:
    """Load or query the API for text-embedding-ada-002 for all texts."""
    embeddings = openai.embeddings_utils.get_embeddings(
        list_of_text=texts,
        engine='text-embedding-ada-002',
    )
    return np.array(embeddings, np.float32)
