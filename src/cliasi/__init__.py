"""Command line utility for coloring text and writing pretty things."""

__author__ = "Qrashi"

from .cliasi import STDERR_STREAM, STDOUT_STREAM, Cliasi, cli
from .constants import SYMBOLS, TextColor
from .logging_handler import install_exception_hook, install_logger

__version__: str
"""Cliasi version fetched from setuptools_scm 
or (if not available) set to '0+unknown'."""

try:
    # Prefer the file written by setuptools_scm at build/install time
    from .__about__ import __version__
except Exception:  # file not generated yet (e.g., fresh clone)
    try:
        # If the package is installed, ask importlib.metadata
        from importlib.metadata import version as _pkg_version

        __version__ = _pkg_version("singlejson")
    except Exception:
        # Last resort for local source trees without SCM metadata
        __version__ = "0+unknown"

install_logger(cli)
install_exception_hook(cli)

__all__ = [
    "Cliasi",
    "cli",
    "install_logger",
    "STDOUT_STREAM",
    "STDERR_STREAM",
    "SYMBOLS"
    "TextColor",
]
