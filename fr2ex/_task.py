"""Shared custom logic for accessing the OpenAI API and caching results."""

__all__ = [
    'ensure_api_key',
    'Task',
    'TaskDecorator',
    'api_task',
]

import contextlib
import functools
import json
import logging
from pathlib import Path
from typing import Protocol, TypeVar

import blake3
import msgpack
import msgpack_numpy
import openai

from fr2ex import paths

_T = TypeVar('_T')
"""Invariant type parameter, used for API task return types."""

_T_co = TypeVar('_T_co', covariant=True)
"""Covariant type parameter, used for API return-type protocol parameters."""

msgpack_numpy.patch()


def _build_path(task_name: str, texts: list[str]) -> Path:
    """Build a pathname with the task name and a blake3 hash of the texts."""
    json_bytes = json.dumps(texts).encode()
    hexdigest = blake3.blake3(json_bytes).hexdigest(length=16)
    return paths.data_dir / f'{task_name}-{hexdigest}.msgpack'


def ensure_api_key() -> None:
    """Load the OpenAI API key from a key file, if it is not yet loaded."""
    if openai.api_key_path is None and openai.api_key is None:
        openai.api_key_path = str(paths.default_api_key_file)


class Task(Protocol[_T_co]):
    """Protocol for callables providing core logic of API tasks."""

    def __call__(self, texts: list[str]) -> _T_co: ...


class TaskDecorator(Protocol):
    """Protocol for callables that decorate a Task, returning another Task."""

    def __call__(self, func: Task[_T]) -> Task[_T]: ...


def api_task(task_name: str) -> TaskDecorator:
    """Decorator factory to load a saved result or query the OpenAI API."""
    def decorator(func: Task[_T]) -> Task[_T]:
        @functools.wraps(func)
        def wrapper(texts: list[str]) -> _T:
            path = _build_path(task_name, texts)

            with contextlib.suppress(FileNotFoundError):
                with open(path, 'rb') as file:
                    logging.info('Reading cached %s.', task_name)
                    return msgpack.unpack(file)

            ensure_api_key()
            logging.info('Querying OpenAI %s endpoint.', task_name)
            results = func(texts)

            with open(path, 'wb') as file:
                msgpack.pack(results, file)

            return results

        return wrapper

    return decorator
