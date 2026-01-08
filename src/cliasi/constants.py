"""
Constants used across the cliasi library.

This module defines animations and default settings for the CLI.
"""

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


ANIMATION_SYMBOL_DEFAULT_FRAMES: list[str] = ["/", "|", "\\", "-"]
ANIMATION_SYMBOL_SMALL_FRAMES: list[str] = ["+", "-", "*"]
ANIMATION_SYMBOL_MOON_FRAMES: list[str] = [
    "🌑",
    "🌒",
    "🌓",
    "🌔",
    "🌕",
    "🌖",
    "🌗",
    "🌘",
]
ANIMATION_MAIN_BIG: dict[str, int | list[str]] = {
    "frame_every": 1,
    "frames": [
        "[|\\____________]",
        "[_|\\___________]",
        "[__|\\__________]",
        "[___|\\_________]",
        "[____|\\________]",
        "[_____|\\_______]",
        "[______|\\______]",
        "[_______|\\_____]",
        "[________|\\____]",
        "[_________|\\___]",
        "[__________|\\__]",
        "[___________|\\_]",
        "[____________|\\]",
        "[____________/|]",
        "[___________/|_]",
        "[__________/|__]",
        "[_________/|___]",
        "[________/|____]",
        "[_______/|_____]",
        "[______/|______]",
        "[_____/|_______]",
        "[____/|________]",
        "[___/|_________]",
        "[__/|__________]",
        "[_/|___________]",
        "[/|____________]",
    ],
}
ANIMATION_MAIN_DEFAULT: dict[str, int | list[str]] = {
    "frame_every": 2,
    "frames": [
        "|#   |",
        "| #  |",
        "|  # |",
        "|   #|",
        "|   #|",
        "|  # |",
        "| #  |",
        "|#   |",
    ],
}

ANIMATIONS_SYMBOLS: list[list[str]] = [
    ANIMATION_SYMBOL_SMALL_FRAMES,
    ANIMATION_SYMBOL_DEFAULT_FRAMES,
    ANIMATION_SYMBOL_MOON_FRAMES,
]

ANIMATIONS_MAIN: list[dict[str, int | list[str]]] = [
    ANIMATION_MAIN_DEFAULT,
    ANIMATION_MAIN_BIG,
]

ANIMATION_SYMBOLS_PROGRESSBAR: dict[str, list[list[str]]] = {
    "default": ANIMATIONS_SYMBOLS,
    "download": [["🢓", "↧", "⭣", "⯯", "⤓", "⩡", "_", "_"]],
}

DEFAULT_TERMINAL_SIZE: int = 80
"""Default terminal size used for CLI rendering."""


class TextColor(StrEnum):
    """Different terminal colors to be used in the CLI."""

    RESET = "\033[0m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_RED = "\033[91m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_WHITE = "\033[97m"


UNICORN = [
    e.value
    for e in TextColor
    if e.name.startswith("BRIGHT_") and e.name not in ["BRIGHT_BLACK", "BRIGHT_WHITE"]
]
"""Colors used for unicorn animation in the CLI."""

SYMBOLS: dict[str, str] = {
    "success": "✔",
    "download": "⤓",
}
"""Symbols used in the CLI for various statuses."""
