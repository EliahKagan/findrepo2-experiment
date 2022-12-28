"""
Computing text embeddings of repository names.

The text embeddings computed are computed with OpenAI's new (in December 2022)
model text-embedding-ada-002.
"""

__all__ = ['EmbeddingsMatrix', 'embed_many']

from nptyping import Float32, NDArray, Shape, assert_isinstance
import numpy as np
import openai.embeddings_utils

from fr2ex import _task

EmbeddingsMatrix = NDArray[Shape['*, 1536'], Float32]
"""A matrix whose rows are embeddings in a 1536-dimensional space."""


@_task.api_task('embeddings')
def embed_many(texts: list[str]) -> EmbeddingsMatrix:
    """Load or query the API for text-embedding-ada-002 for all texts."""
    embeddings = openai.embeddings_utils.get_embeddings(
        list_of_text=texts,
        engine='text-embedding-ada-002',
    )
    matrix = np.array(embeddings, Float32)
    assert_isinstance(matrix, EmbeddingsMatrix)
    return matrix
