from enum import StrEnum

LOADING_SYMBOL = ["/", "|", "\\", "-"]
LOADING_SYMBOL_ALT = ["+", "-", "*"]
LOADING_SYMBOL_MOON = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
LOADING_ANIMATION_ALT = {
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
LOADING_ANIMATION = {
    "frame_every": 2,
    "frames": ["|#   |", "| #  |", "|  # |", "|   #|", "|   #|", "|  # |", "| #  |", "|#   |"]
}

LOADING = {
    "symbol": [
        LOADING_SYMBOL_ALT,
        LOADING_SYMBOL,
        LOADING_SYMBOL_MOON
    ],
    "animation": [
        LOADING_ANIMATION,
        LOADING_ANIMATION_ALT
    ]
}

PROGRESSBAR_LOADING = {
    "default": LOADING["symbol"],
    "download": [
        ["🢓", "↧", "⭣", "⯯", "⤓", "⩡", "_", "_"]
    ]
}

DEFAULT_TERMINAL_SIZE = 80

class Color(StrEnum):
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

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"