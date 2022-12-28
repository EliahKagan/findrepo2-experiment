"""Shared custom logic for accessing the OpenAI API and caching results."""

__all__ = ['DEFAULT_API_KEY_PATH', 'Task', 'TaskDecorator', 'api_task']

import contextlib
import functools
import json
import logging
from typing import Protocol, TypeVar

import blake3
import msgpack
import msgpack_numpy
import openai

DEFAULT_API_KEY_PATH = '.api_key'
"""The default path to look for the OpenAI API key."""

_T = TypeVar('_T')
_T_co = TypeVar('_T_co', covariant=True)

msgpack_numpy.patch()


def _build_filename(task_name: str, texts: list[str]) -> str:
    """Build a filename with the task name and a blake3 hash of the texts."""
    json_bytes = json.dumps(texts).encode()
    hexdigest = blake3.blake3(json_bytes).hexdigest(length=16)
    return f'{task_name}-{hexdigest}.msgpack'


def _ensure_api_key() -> None:
    """Load the OpenAI API key from a key file, if it is not yet loaded."""
    if openai.api_key_path is None and openai.api_key is None:
        openai.api_key_path = DEFAULT_API_KEY_PATH


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
            filename = _build_filename(task_name, texts)

            with contextlib.suppress(FileNotFoundError):
                with open(filename, 'rb') as file:
                    logging.info('Reading cached %s.', task_name)
                    return msgpack.unpack(file)

            _ensure_api_key()
            logging.info('Querying OpenAI %s endpoint.', task_name)
            results = func(texts)

            with open(filename, 'wb') as file:
                msgpack.pack(results, file)

            return results

        return wrapper

    return decorator
