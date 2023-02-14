"""Accessing repository information on the remote server."""

__all__ = ['fetch_repo_names']

import pathlib

import fabric


REPO_DIR = '/repos'
"""Absolute path to the directory on the server where repos are kept."""

GIT_SUFFIX = '.git'
"""The extension to expect, strip from, and restore to repo pathnames."""


def fetch_repo_names() -> list[str]:
    """Obtain a list of repository names from the remote Git server."""
    # Find out the hostname of the server that has the remote repositories.
    config_path = pathlib.Path.home() / '.nrr-frr-server'
    with open(config_path, encoding='utf-8') as file:
        hostname = file.read().strip()

    # List the contents of the "public" repositories directory on that server.
    with fabric.Connection(hostname) as connection:
        entries = connection.sftp().listdir(REPO_DIR)

    # Return names that end in the appropriate suffix, stripping the suffix.
    return sorted(entry.removesuffix(GIT_SUFFIX) for entry in entries
                  if entry.endswith(GIT_SUFFIX))
