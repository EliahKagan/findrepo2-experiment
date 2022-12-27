"""Shared custom logic for accessing the OpenAI API and caching results."""

__all__ = ['DEFAULT_API_KEY_PATH', 'api_task']

import contextlib
import functools
import json
import logging
from typing import Any  # FIXME: Replace uses with specific types.

import blake3
import msgpack
import msgpack_numpy
import openai

msgpack_numpy.patch()

DEFAULT_API_KEY_PATH = '.api_key'
"""The default path to look for the OpenAI API key."""


def _build_filename(task_name: str, texts: list[str]) -> str:
    """Build a filename with the task name and a blake3 hash of the texts."""
    json_bytes = json.dumps(texts).encode()
    hexdigest = blake3.blake3(json_bytes).hexdigest(length=16)
    return f'{task_name}-{hexdigest}.msgpack'


def _ensure_api_key() -> None:
    """Load the OpenAI API key from a key file, if it is not yet loaded."""
    if openai.api_key_path is None and openai.api_key is None:
        openai.api_key_path = DEFAULT_API_KEY_PATH


def api_task(task_name: str) -> Any:
    """Decorator factory to load a saved result or query the OpenAI API."""
    def decorator(func: Any) -> Any:
        @functools.wraps(func)
        def wrapper(texts: list[str]) -> Any:
            filename = _build_filename(task_name, texts)

            with contextlib.suppress(FileNotFoundError):
                with open(filename, 'rb') as file:
                    logging.info(f'Reading cached {task_name}.')
                    return msgpack.unpack(file)

            _ensure_api_key()
            logging.info(f'Querying OpenAI {task_name} endpoint.')
            results = func(texts)

            with open(filename, 'wb') as file:
                msgpack.pack(results, file)

            return results

        return wrapper

    return decorator
