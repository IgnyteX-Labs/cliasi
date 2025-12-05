"""Command line utility for coloring text and writing pretty things."""
__author__ = "Qrashi"

from .cliasi import Cliasi, cli
from .constants import TextColor

try:
    # Prefer the file written by setuptools_scm at build/install time
    from .__about__ import __version__  # type: ignore
except Exception:  # file not generated yet (e.g., fresh clone)
    try:
        # If the package is installed, ask importlib.metadata
        from importlib.metadata import version as _pkg_version
        __version__ = _pkg_version("singlejson")
    except Exception:
        # Last resort for local source trees without SCM metadata
        __version__ = "0+unknown"

SYMBOLS = {
    "success": "✔",
    "download": "⤓",
}

__all__ = ['SYMBOLS', 'Cliasi', 'cli', 'TextColor']
