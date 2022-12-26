"""Shared custom logic for accessing the OpenAI API."""

import openai

__all__ = ['DEFAULT_API_KEY_PATH', 'prepare']

DEFAULT_API_KEY_PATH = '.api_key'
"""The default path to look for the OpenAI API key."""


def prepare() -> None:
    """
    Do general preparation to use the OpenAI API.

    Currently this just ensures the API key is loaded.
    """
    if openai.api_key_path is None and openai.api_key is None:
        openai.api_key_path = DEFAULT_API_KEY_PATH
