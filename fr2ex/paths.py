"""Paths used in modules and notebooks."""

__all__ = ['default_api_key_file', 'data_dir']

from pathlib import Path

_fixed_parent_path = Path(__file__).absolute().parent.parent
"""The parent directory of the directory that contains this module."""

default_api_key_file = _fixed_parent_path / '.api_key'
"""The default path for a file that contains the OpenAI API key."""

data_dir = _fixed_parent_path / 'data'
"""The directory where we keep the saved data files (the cache)."""
