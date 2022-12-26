"""Shared custom logic for accessing the OpenAI API."""

import functools
from typing import Callable, ParamSpec, TypeVar

import openai

__all__ = ['DEFAULT_API_KEY_PATH', 'uses_api']

DEFAULT_API_KEY_PATH = '.api_key'
"""The default path to look for the OpenAI API key."""

_In = ParamSpec('_In')
_Out = TypeVar('_Out')


def uses_api(func: Callable[_In, _Out]) -> Callable[_In, _Out]:
    """
    Decorate a function so it does general preparation to use the OpenAI API.

    Currently the preparation consists just of ensuring the API key is loaded.
    """
    @functools.wraps(func)
    def wrapper(*args: _In.args, **kwargs: _In.kwargs) -> _Out:
        if openai.api_key_path is None and openai.api_key is None:
            openai.api_key_path = DEFAULT_API_KEY_PATH
        return func(*args, **kwargs)

    return wrapper
