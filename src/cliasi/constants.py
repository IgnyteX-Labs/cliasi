"""
Constants used across the cliasi library.

This module defines animations and default settings for the CLI.
"""

from enum import StrEnum
from typing import List, Dict, Union

ANIMATION_SYMBOL_DEFAULT_FRAMES = ["/", "|", "\\", "-"]
ANIMATION_SYMBOL_SMALL_FRAMES = ["+", "-", "*"]
ANIMATION_SYMBOL_MOON_FRAMES = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
ANIMATION_MAIN_BIG = {
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
        "[/|____________]"
    ]
}
ANIMATION_MAIN_DEFAULT = {
    "frame_every": 2,
    "frames": ["|#   |", "| #  |", "|  # |", "|   #|", "|   #|", "|  # |", "| #  |", "|#   |"]
}

ANIMATIONS_SYMBOLS: List[List[str]] = [
    ANIMATION_SYMBOL_SMALL_FRAMES,
    ANIMATION_SYMBOL_DEFAULT_FRAMES,
    ANIMATION_SYMBOL_MOON_FRAMES
]

ANIMATIONS_MAIN: List[Dict[str, Union[int, List[str]]]] = [
    ANIMATION_MAIN_DEFAULT,
    ANIMATION_MAIN_BIG
]

ANIMATION_SYMBOLS_PROGRESSBAR = {
    "default": ANIMATIONS_SYMBOLS,
    "download": [
        ["🢓", "↧", "⭣", "⯯", "⤓", "⩡", "_", "_"]
    ]
}

DEFAULT_TERMINAL_SIZE = 80


class TextColor(StrEnum):
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


UNICORN = [e.value for e in TextColor if
           e.name.startswith("BRIGHT_") and not (e.name in ["BRIGHT_BLACK", "BRIGHT_WHITE"])]
