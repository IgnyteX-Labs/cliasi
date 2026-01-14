import builtins
import logging
import sys
import textwrap
from collections.abc import Callable
from getpass import getpass
from random import randint
from threading import Event, Lock, Thread
from time import sleep
from typing import TextIO

from .constants import (
    ANIMATION_SYMBOLS_PROGRESSBAR,
    ANIMATIONS_MAIN,
    ANIMATIONS_SYMBOLS,
    DEFAULT_TERMINAL_SIZE,
    UNICORN,
    CursorPos,
    TextColor,
)

_print_lock: Lock = Lock()

STDOUT_STREAM: TextIO
"""Default stdout stream for cliasi messages. Used by all Cliasi instances"""
STDOUT_STREAM = sys.stdout
STDERR_STREAM: TextIO
"""Default stderr stream for cliasi messages. Used by all Cliasi instances"""
STDERR_STREAM = sys.stderr

# Try to get the terminal size
try:
    import os
    import shutil

    cols = int(os.environ.get("COLUMNS", 80))
    rows = int(os.environ.get("LINES", 24))

    def _terminal_size() -> int:
        return shutil.get_terminal_size(fallback=(cols, rows))[0]
        # [0] for cols

    _terminal_size()  # Try if getting terminal size works

except Exception as e:
    print("! [cliasi] Error: Could not retrieve terminal size!", e)

    def _terminal_size() -> int:
        return DEFAULT_TERMINAL_SIZE


class Cliasi:
    """A Cliasi CLI instance.
    Stores display settings and a minimum verbosity threshold."""

    min_verbose_level: int
    messages_stay_in_one_line: bool
    enable_colors: bool
    max_dead_space: int | None
    __prefix_seperator: str
    __space_before_message: int  # Number of spaces before message start (for alignment)

    def __init__(
        self,
        prefix: str = "",
        messages_stay_in_one_line: bool = False,
        colors: bool = True,
        min_verbose_level: int | None = None,
        seperator: str = "|",
        max_dead_space: int | None = 100,
    ):
        """
        Initialize a cliasi instance.

        :param prefix: Message Prefix [prefix] message
        :param messages_stay_in_one_line:
            Have all messages appear in one line by default
        :param colors: Enable color display
        :param min_verbose_level:
            Only displays messages with verbose level higher
            than this value (default is logging.INFO),
            None will result in the verbosity level
            getting set to the value of the global instance which is by default 0
        :param seperator: Seperator between prefix and message
        :param max_dead_space:
            Sets the maximum dead space (space characters) allowed when a message
            uses alignments. Too much dead space will cause people to not read
            aligned messages. Set to None to disable.
        """
        self.__prefix = ""
        self.messages_stay_in_one_line = messages_stay_in_one_line
        self.enable_colors = colors
        self.min_verbose_level = (
            min_verbose_level
            if min_verbose_level is not None
            else cli.min_verbose_level
        )
        self.__prefix_seperator = seperator
        self.max_dead_space = max_dead_space
        self.set_prefix(prefix)

    def __compute_space_before_message(self) -> None:
        """
        Compute empty space before message for alignment WITHOUT symbol!

        :return: None
        """
        # symbol + space (1) + prefix + space(2) + separator + space (3) -> message
        self.__space_before_message = (
            3 + len(self.__prefix) + len(self.__prefix_seperator)
        )

    def set_seperator(self, seperator: str) -> None:
        """
        Set the seperator between prefix and message

        :param seperator: Seperator, usually only one character
        :return: None
        """
        self.__prefix_seperator = seperator
        self.__compute_space_before_message()

    def set_prefix(self, prefix: str) -> None:
        """
        Update the message prefix of this instance.
        Prefixes should be three letters long but do as you wish.

        :param prefix: New message prefix without brackets []
        :return: None
        """
        self.__prefix = f"[{prefix}]"
        self.__compute_space_before_message()

    def __verbose_check(self, level: int) -> bool:
        """
        Check if message should be interrupted by verbose level.

        :param level: given verbosity level
        :return: False if message should be sent, true if message should not be sent
        """
        return level < self.min_verbose_level

    def __print(
        self,
        color: TextColor | str,
        symbol: str,
        message_left: str | bool,
        override_messages_stay_in_one_line: bool | None,
        message_center: str | bool = False,
        message_right: str | bool = False,
        color_message: bool = True,
        write_to_stderr: bool = False,
    ) -> dict[str, int] | None:
        """
        Print message to the console with word wrapping and customizable separators.
        If parameters left, center, and right are None, this will do nothing.

        :param color: Color to print message and symbol with (ASCII escape code)
        :param symbol: Symbol to print at the start of the message
        :param message_left:
            Message or bool flag to print on left side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param color_message: Print the main message with color
        :param write_to_stderr: Write message to stderr instead of stdout
        :return: Metadata about the printed line (alignments) or None
        """
        oneline = (
            self.messages_stay_in_one_line
            if override_messages_stay_in_one_line is None
            else override_messages_stay_in_one_line
        )
        preamble_len = self.__space_before_message + len(symbol) + 1
        content_space = _terminal_size() - preamble_len
        # space(1) + symbol + space_before_message (prefix + seperator) -> message

        reset_message_left = False
        if isinstance(message_center, bool) and message_center:
            # flag set
            message_center = message_left
            reset_message_left = True
        if isinstance(message_right, bool) and message_right:
            # flag set
            message_right = message_left
            reset_message_left = True
        if reset_message_left:
            message_left = ""

        content_total = message_left if isinstance(message_left, str) else ""
        content_total += message_center if isinstance(message_center, str) else ""
        content_total += message_right if isinstance(message_right, str) else ""

        seperating_space = (
            1 if (isinstance(message_left, str) and message_left != "") else 0
        )
        seperating_space += (
            1 if (isinstance(message_center, str) and message_center != "") else 0
        )
        seperating_space += (
            1 if (isinstance(message_right, str) and message_right != "") else 0
        )

        seperating_space -= 1  # elements - 1 = seperating_space

        lines = []

        if content_total == "":
            # Nothing to print
            return None
        # content_space - seperating space (needed to separate left, right etc)
        if (content_space - seperating_space) < len(
            content_total
        ) or "\n" in content_total:
            # Can't print in one line.
            content_to_split = ""
            if isinstance(message_left, str):
                content_to_split += message_left
            if isinstance(message_center, str):
                content_to_split += (
                    " " + message_center
                    if isinstance(message_left, str) and message_left != ""
                    else message_center
                )  # Add space only if message_left is set
            if isinstance(message_right, str) and (
                len(message_right) > content_space  # too long -> no alignment
                or "\n" in message_right  # multiline -> no alignment attempt
            ):
                # message_right won't be aligned due to it being multiline
                content_to_split += (
                    " " + message_right
                    if (
                        (isinstance(message_left, str) and message_left != "")
                        or (isinstance(message_center, str) and message_center != "")
                        # Only if one of the previous ones exists
                    )
                    else message_right
                )

                for paragraph in content_to_split.splitlines():
                    wrapped = textwrap.wrap(paragraph, width=content_space)
                    if wrapped:
                        lines.extend(wrapped)
                    else:
                        lines.append("")

                # right aligned content not alignable -> no alignment.
                left_end = len(lines[-1])
                center_end = len(lines[-1])
                right_end = len(lines[-1])
                # CursorPos alignment not possible because message_right is multiline
                # we are done test_right_multiline_too_long

            else:
                # right message might be alignable
                for paragraph in content_to_split.splitlines():
                    wrapped = textwrap.wrap(paragraph, width=content_space)
                    if wrapped:
                        lines.extend(wrapped)
                    else:
                        lines.append("")
                # left and center are together in one string
                # see if the last line has space for right message_right
                if (
                    isinstance(message_right, str)
                    and len(lines[-1]) + len(message_right) + 1 <= content_space
                ):
                    # Alignment possible on the last row
                    left_end = len(lines[-1])  # left and center end at len of last line
                    center_end = len(lines[-1])
                    lines[-1] = (
                        lines[-1]
                        + " " * (content_space - len(lines[-1]) - len(message_right))
                        + message_right
                    )

                    # right_aligned content aligned on last line
                    right_end = len(lines[-1])
                # CursorPos alignment not possible because message_right is multiline
                # we are done test_right_fit_last_line

                elif isinstance(message_right, str):
                    # Alignment not possible, append message_right
                    for paragraph in (lines.pop() + " " + message_right).splitlines():
                        wrapped = textwrap.wrap(paragraph, width=content_space)
                        if wrapped:
                            lines.extend(wrapped)
                        else:
                            lines.append("")

                    # right aligned content not alignable -> no alignment.
                    left_end = len(lines[-1])
                    center_end = len(lines[-1])
                    right_end = len(lines[-1])
                    # CursorPos alignment not possible because message_right got
                    # multiline due to left + center being too long
                    # we are done test_right_no_fit_last_line

                else:
                    left_end = len(lines[-1])
                    center_end = len(lines[-1])
                    right_end = len(lines[-1])

            #

        else:
            # All content is alignable in one line
            m_left = message_left if isinstance(message_left, str) else ""
            m_center = message_center if isinstance(message_center, str) else ""
            m_right = message_right if isinstance(message_right, str) else ""
            if (
                isinstance(self.max_dead_space, int)  # Logic is enabled
                and message_left is not False  # Left message not disabled deliberately
                and (content_space - len(content_total) - seperating_space)
                > self.max_dead_space
            ):
                # Too much dead space, print one after the other
                lines.append(
                    m_left
                    + (" " if m_left and m_center else "")
                    + m_center
                    + (" " if (m_left or m_center) and m_right else "")
                    + m_right
                )
                left_end = len(lines[-1])
                center_end = len(lines[-1])
                right_end = len(lines[-1])
            else:
                line = m_left
                left_end = len(line)

                if m_center:
                    center_start = (content_space - len(m_center)) // 2
                    needed_space = 1 if m_left else 0
                    if center_start >= len(line) + needed_space:
                        line += " " * (center_start - len(line)) + m_center
                    else:
                        line += (" " if m_left else "") + m_center
                    center_end = len(line)
                else:
                    center_end = left_end

                if m_right:
                    right_start = content_space - len(m_right)
                    needed_space = 1 if (m_left or m_center) else 0
                    if right_start >= len(line) + needed_space:
                        line += " " * (right_start - len(line)) + m_right
                    else:
                        line += (" " if (m_left or m_center) else "") + m_right
                    right_end = len(line)
                else:
                    right_end = center_end

                lines.append(line)

        with _print_lock:
            index = 0
            for line in lines:
                index += 1
                is_last = index == len(lines)
                end_str = ("" if (oneline and is_last) else "\n") + TextColor.RESET

                if index == 1:
                    # Printing first / last line
                    print(
                        "\r\x1b[2K\r",
                        (color if self.enable_colors else "") + symbol,
                        TextColor.DIM + self.__prefix + TextColor.RESET,
                        self.__prefix_seperator
                        + (color if self.enable_colors and color_message else ""),
                        line,
                        file=STDERR_STREAM if write_to_stderr else STDOUT_STREAM,
                        end=end_str,
                        flush=True,
                    )
                else:
                    # Printing multiline strings
                    # prefix, and symbol are replaced with spaces
                    print(
                        "\r\x1b[2K\r",
                        # space (done because new print function argument)
                        # + symbol
                        # + space (1)
                        # + prefix
                        # + space (not done because new argument)
                        " " * (len(self.__prefix) + len(symbol) + 1),
                        self.__prefix_seperator,
                        (color if self.enable_colors and color_message else "") + line,
                        file=STDERR_STREAM if write_to_stderr else STDOUT_STREAM,
                        end=end_str,
                        flush=True,
                    )

        return {
            "left_end": preamble_len + left_end,
            "center_end": preamble_len + center_end,
            "right_end": preamble_len + right_end,
            "total_length": preamble_len + len(lines[-1]),
        }

    def message(
        self,
        message_left: str | bool,
        verbosity: int = logging.INFO,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Send a message in format # [prefix] message

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param verbosity: Verbosity of this message
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.WHITE + TextColor.DIM,
            "#",
            message_left,
            override_messages_stay_in_one_line,
            message_center=message_center,
            message_right=message_right,
            color_message=False,
        )

    def info(
        self,
        message_left: str | bool,
        verbosity: int = logging.INFO,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Print an informational message.
        Send an info message in format i [prefix] message

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param verbosity: Verbosity of this message
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.BRIGHT_WHITE,
            "i",
            message_left,
            override_messages_stay_in_one_line,
            message_center=message_center,
            message_right=message_right,
            color_message=False,
        )

    def log(
        self,
        message_left: str | bool,
        verbosity: int = logging.DEBUG,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Send a log message in format LOG [prefix] message

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param verbosity: Verbosity of this message
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.WHITE + TextColor.DIM,
            "LOG",
            message_left,
            override_messages_stay_in_one_line,
            message_center=message_center,
            message_right=message_right,
            color_message=False,
        )

    def log_small(
        self,
        message_left: str | bool,
        verbosity: int = logging.DEBUG,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Send a log message in format LOG [prefix] message

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param verbosity: Verbosity of this message
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.WHITE + TextColor.DIM,
            "L",
            message_left,
            override_messages_stay_in_one_line,
            message_center=message_center,
            message_right=message_right,
            color_message=False,
        )

    def list(
        self,
        message_left: str | bool,
        verbosity: int = logging.INFO,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Send a list style message in format * [prefix] message

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param verbosity: Verbosity of this message
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.BRIGHT_WHITE,
            "-",
            message_left,
            override_messages_stay_in_one_line,
            message_center=message_center,
            message_right=message_right,
            color_message=False,
        )

    def warn(
        self,
        message_left: str | bool,
        verbosity: int = logging.WARNING,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Send a warning message in format ! [prefix] message

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param verbosity: Verbosity of this message
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.BRIGHT_YELLOW,
            "!",
            message_left,
            override_messages_stay_in_one_line,
            message_center=message_center,
            message_right=message_right,
        )

    def fail(
        self,
        message_left: str | bool,
        verbosity: int = logging.CRITICAL,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Send a failure message in format X [prefix] message

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param verbosity: Verbosity of this message
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.BRIGHT_RED,
            "X",
            message_left,
            override_messages_stay_in_one_line,
            message_center=message_center,
            message_right=message_right,
            write_to_stderr=True,
        )

    def success(
        self,
        message_left: str | bool,
        verbosity: int = logging.INFO,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Send a success message in format ✔ [prefix] message

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param verbosity: Verbosity of this message
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.BRIGHT_GREEN,
            "✔",
            message_left,
            override_messages_stay_in_one_line,
            message_center=message_center,
            message_right=message_right,
        )

    @staticmethod
    def newline() -> None:
        """
        Print a newline.

        :return: None
        """
        print("", file=STDOUT_STREAM, flush=True)

    def ask(
        self,
        message_left: str | bool,
        hide_input: bool = False,
        message_center: str | bool = False,
        message_right: str | bool = False,
        override_messages_stay_in_one_line: bool | None = None,
        cursor_position: CursorPos = CursorPos.LEFT,
    ) -> str:
        """
        Ask for input in format ? [prefix] message

        :param message_left:
            Question to ask
            Can also be a bool flag to print left-aligned.
        :param hide_input: True hides user input
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.

        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :param cursor_position:
            Cursor position of input cursor
            Only available when output is not longer than one line OR
            if last line has space for message_right and the cursor position
            is LEFT or RIGHT
        :return: The user input as a string.
        """

        metadata = self.__print(
            TextColor.BRIGHT_MAGENTA if hide_input else TextColor.MAGENTA,
            "?",
            message_left,
            True,
            message_center=message_center,
            message_right=message_right,
        )

        if metadata and cursor_position != CursorPos.RIGHT:
            target = (
                metadata["left_end"]
                if cursor_position == CursorPos.LEFT
                else metadata["center_end"]
            )
            walk_back = metadata["total_length"] - target
            if walk_back > 0:
                print(f"\x1b[{walk_back}D", end="", flush=True)
        if hide_input:
            result = getpass(" ")
        else:
            result = input(" ")
        oneline = (
            self.messages_stay_in_one_line
            if override_messages_stay_in_one_line is None
            else override_messages_stay_in_one_line
        )
        if oneline:
            print("\x1b[1A\x1b[2K", end="")
        return result

    def __show_animation_frame(
        self,
        message_left: str | bool,
        message_center: str | bool,
        message_right: str | bool,
        color: TextColor | str,
        current_symbol_frame: str,
        current_animation_frame: str,
    ) -> None:
        """
        Show a single animation frame based on the total index

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param color: Color of message
        :param current_symbol_frame: Current symbol animation to show
        :param current_animation_frame: Current animation frame to show
        :return: None
        """
        self.__print(
            color,
            current_symbol_frame,
            current_animation_frame
            + ("" if current_animation_frame == "" else " ")
            + message_left
            if isinstance(message_left, str)
            else "",
            True,
            message_center=message_center,
            message_right=message_right,
        )

    def animate_message_blocking(
        self,
        message_left: str,
        time: int | float,
        message_center: str | bool = False,
        message_right: str | bool = False,
        verbosity: int = logging.INFO,
        interval: int | float = 0.25,
        unicorn: bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> None:
        """
        Display a loading animation for a fixed time
        This will block the main thread using time.sleep

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param time: Time to display for
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param verbosity: Verbosity of this message
        :param interval: Interval between changes in loading animation
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """

        if self.__verbose_check(verbosity):
            return

        remaining = time
        selection_symbol, selection_animation = (
            randint(0, len(ANIMATIONS_SYMBOLS) - 1),
            randint(0, len(ANIMATIONS_MAIN) - 1),
        )
        symbol_frames = ANIMATIONS_SYMBOLS[selection_symbol]
        frames = ANIMATIONS_MAIN[selection_animation]["frames"]
        if not isinstance(frames, list):
            self.warn(
                f"CLIASI error: "
                f"Animation frames must be a list, got {type(frames).__name__}."
                f" Falling back to default frames.",
                override_messages_stay_in_one_line=False,
            )
        animation_frames: list[str] = frames if isinstance(frames, list) else ["*", "-"]
        index_total = 0
        while remaining > 0:
            frame_every_val = ANIMATIONS_MAIN[selection_animation]["frame_every"]
            if not isinstance(frame_every_val, int):
                self.warn(
                    f"CLIASI error: "
                    f"frame_every must be an int, got {type(frame_every_val).__name__}."
                    f" Falling back to 1.",
                    override_messages_stay_in_one_line=False,
                )
            frame_every: int = (
                frame_every_val if isinstance(frame_every_val, int) else 1
            )
            self.__show_animation_frame(
                message_left,
                message_center,
                message_right,
                TextColor.BRIGHT_MAGENTA
                if not unicorn
                else UNICORN[index_total % len(UNICORN)],
                symbol_frames[index_total % len(symbol_frames)],
                animation_frames[(index_total // frame_every) % len(animation_frames)],
            )
            index_total += 1

            remaining -= interval
            if remaining < interval:
                break

            sleep(interval)

        sleep(remaining)
        oneline = (
            self.messages_stay_in_one_line
            if override_messages_stay_in_one_line is None
            else override_messages_stay_in_one_line
        )
        if not oneline:
            print("")

    def __format_progressbar_to_screen_width(
        self, message: str, symbol: str, progress: int, show_percent: bool
    ) -> str:
        """
        Returns a string representation of the progress bar
        Like this [====message===] xx%

        :param message: Message to display
        :param symbol: Symbol to get symbol length
        :param progress: Progress to display
        :param show_percent: Show percentage at end of bar
        :return: String representation of the progress bar
        """
        try:
            p = int(progress)
        except ValueError:
            p = 0
        dead_space = (
            1
            + len(symbol)
            + self.__space_before_message
            + (len(f" {p}%") if show_percent else 0)
        )
        # space(1)
        # + symbol
        # + space_before_message (prefix + seperator) -> message
        # (+ space + percent if needed)

        # Clamp progress
        p = max(0, min(100, progress))

        # Determine available width for the bar content (inside the brackets)
        total_cols = _terminal_size()

        inside_width = max(8, total_cols - max(0, dead_space) - 3)

        # Prepare message to fit, centered, without overlapping percent area
        # Compute the maximum width available for message without touching percent area
        max_message_width = max(0, inside_width)
        msg = message if message is not None else ""
        if len(msg) > max_message_width:
            # Truncate with ellipsis if possible
            if max_message_width >= 3:
                msg = msg[: max_message_width - 1] + "…"
            else:
                msg = msg[:max_message_width]
        M = len(msg)

        # Determine message start so that it is centered within the space
        # that excludes the percent area on the far right
        # We consider the layout as: [ left | message | middle | percent | right(end) ]
        # Center message within the first (inside_width - percent_len) columns
        usable_width = inside_width
        msg_start = max(0, (usable_width - M) // 2)
        msg_end = msg_start + M

        # Build a base array of spaces
        bar = [" "] * inside_width

        # Place message
        if M > 0:
            bar[msg_start:msg_end] = list(msg)

        # Place percent text at the very end

        # Compute how many cells should be marked as progressed
        target_fill = round((p / 100.0) * inside_width)

        # Fill with '=' from left to right, but never overwrite message or percent
        for i in range(target_fill):
            # Skip positions occupied by message
            if msg_start <= i < msg_end:
                continue
            bar[i] = "="

        # Wrap with brackets
        return "[" + "".join(bar) + "]" + (f" {p}%" if show_percent else "")

    def progressbar(
        self,
        message: str,
        verbosity: int = logging.INFO,
        progress: int = 0,
        override_messages_stay_in_one_line: bool | None = True,
        show_percent: bool = False,
    ) -> None:
        """
        Display a progress bar with specified progress
        This requires grabbing the correct terminal width
        This is not animated. Call it multiple times to update

        :param message: Message to display
        :param verbosity: Verbosity to display
        :param progress: Progress to display
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :param show_percent: Show percent next to the progressbar
        :return: None
        """

        if self.__verbose_check(verbosity):
            return
        # Print the bar.
        # Keep it on one line unless overridden by override_messages_stay_in_one_line.
        self.__print(
            TextColor.BLUE,
            "#",
            self.__format_progressbar_to_screen_width(
                message, "#", progress, show_percent
            ),
            override_messages_stay_in_one_line,
        )

    def progressbar_download(
        self,
        message: str,
        verbosity: int = logging.INFO,
        progress: int = 0,
        show_percent: bool = False,
        override_messages_stay_in_one_line: bool | None = True,
    ) -> None:
        """
        Display a download bar with specified progress
        This is not animated. Call it multiple times to update

        :param message: Message to display
        :param verbosity: Verbosity to display
        :param progress: Progress to display
        :param show_percent: Show percent next to the progressbar
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: None
        """

        if self.__verbose_check(verbosity):
            return

        self.__print(
            TextColor.BRIGHT_CYAN,
            "⤓",
            self.__format_progressbar_to_screen_width(
                message, "⤓", progress, show_percent
            ),
            override_messages_stay_in_one_line,
        )

    class NonBlockingAnimationTask:
        """
        Defines a non-blocking animation task run on another Thread
        """

        _message_stays_in_one_line: bool
        _condition: Event
        _message_left: str | bool  # Current message to display
        _message_center: str | bool  # Current message to display
        _message_right: str | bool  # Current message to display
        _index: int = 0  # Animation frame total index
        _thread: Thread
        _update: Callable[
            [], None
        ]  # Update call to update with current animation frame

        def __init__(
            self,
            message_left: str | bool,
            message_center: str | bool,
            message_right: str | bool,
            stop_condition: Event,
            message_stays_in_one_line: bool,
        ) -> None:
            self._message_left = message_left
            self._message_center = message_center
            self._message_right = message_right
            self._message_stays_in_one_line = message_stays_in_one_line
            self._condition = stop_condition

        def stop(self) -> None:
            """
            Stop the current animation task

            :return:
            """
            self._condition.set()
            self._thread.join()
            if not self._message_stays_in_one_line:
                print("")

        def update(self, message: str | None = None) -> None:
            """
            Update message of animation

            :param message: Message to update to (None for no update)
            :return: None
            """
            self._message_left = message if message is not None else self._message_left
            self._update()

    def __get_animation_task(
        self,
        message_left: str | bool,
        message_center: str | bool,
        message_right: str | bool,
        color: TextColor,
        symbol_animation: builtins.list[str],
        main_animation: dict[str, int | builtins.list[str]],
        interval: int | float,
        unicorn: bool = False,
        override_messages_stay_in_one_line: bool | None = True,
    ) -> NonBlockingAnimationTask:
        """
        Create an animation task

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param color: Color of message
        :param symbol_animation:
            The symbol animation to display as string frames in a list
        :param main_animation: The main animation to display as string frames in a list
        :param interval: The interval to display as string frames in a list
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line: Override message to stay in one line
        :return A NonBlockingAnimationTask
        """
        condition = Event()

        task = Cliasi.NonBlockingAnimationTask(
            message_left,
            message_center,
            message_right,
            condition,
            override_messages_stay_in_one_line
            if override_messages_stay_in_one_line is not None
            else self.messages_stay_in_one_line,
        )

        def update() -> None:
            """
            Update the animation to the current frame

            :return: None
            """
            frames_val = main_animation["frames"]
            if not isinstance(frames_val, list):
                self.warn(
                    f"CLIASI error: "
                    f"Animation frames must be a list, got {type(frames_val).__name__}."
                    f" Falling back to default frames.",
                    override_messages_stay_in_one_line=False,
                )
            frames: list[str] = (
                frames_val if isinstance(frames_val, list) else ["*", "-"]
            )
            frame_every_val = main_animation["frame_every"]
            if not isinstance(frame_every_val, int):
                self.warn(
                    f"CLIASI error: "
                    f"frame_every must be an int, got {type(frame_every_val).__name__}."
                    f" Falling back to 1.",
                    override_messages_stay_in_one_line=False,
                )
            frame_every: int = (
                frame_every_val if isinstance(frame_every_val, int) else 1
            )

            self.__show_animation_frame(
                task._message_left,
                task._message_center,
                task._message_right,
                color if not unicorn else UNICORN[task._index % len(UNICORN)],
                symbol_animation[task._index % len(symbol_animation)],
                frames[(task._index // frame_every) % len(frames)],
            )

        def animate() -> None:
            """
            Main animation task to be run in thread

            :return: None
            """
            while not condition.is_set():
                task.update()
                task._index += 1
                condition.wait(timeout=interval)

        thread = Thread(target=animate, daemon=True)
        task._thread = thread
        task._update = update
        thread.start()
        return task

    def animate_message_non_blocking(
        self,
        message_left: str | bool,
        message_center: str | bool = False,
        message_right: str | bool = False,
        verbosity: int = logging.INFO,
        interval: int | float = 0.25,
        unicorn: bool = False,
        override_messages_stay_in_one_line: bool | None = None,
    ) -> NonBlockingAnimationTask | None:
        """
        Display a loading animation in the background
        Stop animation by calling .stop() on the returned object

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param verbosity: Verbosity of message
        :param interval: Interval for animation to play
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: NonBlockingAnimationTask if verbosity requirement is met.
        """

        if self.__verbose_check(verbosity):
            return self.__get_null_task()

        selection_symbol, selection_animation = (
            randint(0, len(ANIMATIONS_SYMBOLS) - 1),
            randint(0, len(ANIMATIONS_MAIN) - 1),
        )
        return self.__get_animation_task(
            message_left,
            message_center,
            message_right,
            TextColor.BRIGHT_MAGENTA,
            ANIMATIONS_SYMBOLS[selection_symbol],
            ANIMATIONS_MAIN[selection_animation],
            interval,
            unicorn,
            override_messages_stay_in_one_line,
        )

    def animate_message_download_non_blocking(
        self,
        message_left: str | bool,
        message_center: str | bool = False,
        message_right: str | bool = False,
        verbosity: int = logging.INFO,
        interval: int | float = 0.25,
        unicorn: bool = False,
        override_messages_stay_in_one_line: bool | None = True,
    ) -> NonBlockingAnimationTask | None:
        """
        Display a downloading animation in the background

        :param message_left:
            Message to send or bool flag to print left-aligned.
            See message_center and message_right for details.
        :param message_center:
            Message or bool flag to print centered to terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param message_right:
            Message or bool flag to print on right side of terminal
            If messages dont fit into their sections
            or messages are multiline, they will be outputted one
            after the other (except for right aligned content)
            thus destroying any alignment.
        :param verbosity: Verbosity of message
        :param interval: Interval for animation to play
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: A NonBlockingAnimationTask if verbosity requirement is met.
        """

        if self.__verbose_check(verbosity):
            return self.__get_null_task()

        selection_animation = randint(0, len(ANIMATIONS_MAIN) - 1)
        return self.__get_animation_task(
            message_left,
            message_center,
            message_right,
            TextColor.BRIGHT_CYAN,
            ANIMATION_SYMBOLS_PROGRESSBAR["download"][
                randint(0, len(ANIMATION_SYMBOLS_PROGRESSBAR["download"]) - 1)
            ],
            ANIMATIONS_MAIN[selection_animation],
            interval,
            unicorn,
            override_messages_stay_in_one_line,
        )

    class NonBlockingProgressTask(NonBlockingAnimationTask):
        """
        Defines a non-blocking animation task with a progress bar run on another Thread
        """

        _progress: int

        def __init__(
            self,
            message: str,
            stop_condition: Event,
            override_messages_stay_in_one_line: bool,
            progress: int,
        ) -> None:
            super().__init__(
                message,
                False,
                False,
                stop_condition,
                override_messages_stay_in_one_line,
            )
            # alignment currently not supported in progressbars
            self._progress = progress

        def update(
            self,
            message: str | None = None,
            progress: int | None = None,
            *args: object,
            **kwargs: object,
        ) -> None:
            """
            Update progressbar message and progress

            :param message: Message to update to (None for no update)
            :param progress: Progress to update to (None for no update)
            :return: None
            """
            self._progress = progress if progress is not None else self._progress
            super(Cliasi.NonBlockingProgressTask, self).update(message)

    @staticmethod
    def __get_null_task() -> NonBlockingProgressTask:
        """
        Get a null progressbar task to return when verbosity is not met
        to not return None

        :return: "fake" NonBlockingProgressTask
        """
        task = Cliasi.NonBlockingProgressTask("", Event(), False, 0)

        def _null_update(*args: object, **kwargs: object) -> None:
            pass

        task._update = _null_update

        def _null_stop() -> None:
            pass

        task.stop = _null_stop  # type: ignore[method-assign]
        return task

    def __get_progressbar_task(
        self,
        message: str,
        progress: int,
        symbol_animation: builtins.list[str],
        show_percent: bool,
        interval: int | float,
        color: TextColor,
        unicorn: bool = False,
        override_messages_stay_in_one_line: bool | None = True,
    ) -> NonBlockingProgressTask:
        """
        Get a progressbar task

        :param message: Message to display
        :param progress: Initial progress
        :param symbol_animation: List of string for symbol animation
        :param show_percent: Show percent at end of progressbar
        :param interval: Interval for animation to play
        :param color: Color of progressbar
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line
        :return: NonBlockingProgressTask
        """

        condition = Event()

        task = Cliasi.NonBlockingProgressTask(
            message,
            condition,
            override_messages_stay_in_one_line
            if override_messages_stay_in_one_line is not None
            else self.messages_stay_in_one_line,
            progress,
        )

        def update_bar() -> None:
            """
            Update only the progressbar section of the animation.

            :return: None
            """
            current_symbol = symbol_animation[task._index % len(symbol_animation)]
            self.__show_animation_frame(
                self.__format_progressbar_to_screen_width(
                    message, current_symbol, task._progress, show_percent
                ),
                False,
                False,
                color if not unicorn else UNICORN[task._index % len(UNICORN)],
                current_symbol,
                current_animation_frame="",
            )

        def animate() -> None:
            """
            Animate the progressbar

            :return: None
            """
            while not condition.is_set():
                task.update()
                task._index += 1
                condition.wait(timeout=interval)

        thread = Thread(target=animate, args=(), daemon=True)
        task._thread = thread
        task._update = update_bar
        thread.start()
        return task

    def progressbar_animated_normal(
        self,
        message: str,
        verbosity: int = logging.INFO,
        progress: int = 0,
        interval: int | float = 0.25,
        show_percent: bool = False,
        unicorn: bool = False,
        override_messages_stay_in_one_line: bool | None = True,
    ) -> NonBlockingProgressTask:
        """
        Display an animated progressbar
        Update progress using the returned Task object

        :param message: Message to display
        :param verbosity: Verbosity of message
        :param interval: Interval between animation frames
        :param progress: Current Progress to display
        :param show_percent: Show percent next to the progressbar
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line

        :return:
            :class:`NonBlockingProgressTask` on which you can call
            :meth:`~cliasi.Cliasi.NonBlockingProgressTask.update()` and
            :meth:`~cliasi.Cliasi.NonBlockingProgressTask.stop()`
        :rtype: ~cliasi.Cliasi.NonBlockingProgressTask
        """

        if self.__verbose_check(verbosity):
            return self.__get_null_task()

        return self.__get_progressbar_task(
            message,
            progress,
            ANIMATION_SYMBOLS_PROGRESSBAR["default"][
                randint(0, len(ANIMATION_SYMBOLS_PROGRESSBAR["default"]) - 1)
            ],
            show_percent,
            interval,
            TextColor.BLUE,
            unicorn,
            override_messages_stay_in_one_line,
        )

    def progressbar_animated_download(
        self,
        message: str,
        verbosity: int = logging.INFO,
        progress: int = 0,
        interval: int | float = 0.25,
        show_percent: bool = False,
        unicorn: bool = False,
        override_messages_stay_in_one_line: bool | None = True,
    ) -> NonBlockingProgressTask:
        """
        Display an animated progressbar
        Update progress using the returned Task object

        :param message: Message to display
        :param verbosity: Verbosity of message
        :param interval: Interval between animation frames
        :param progress: Current Progress to display
        :param show_percent: Show percent next to the progressbar
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line:
            Override the message to stay in one line

        :return:
            :class:`NonBlockingProgressTask` on which you can call
            :meth:`~cliasi.Cliasi.NonBlockingProgressTask.update()` and
            :meth:`~cliasi.Cliasi.NonBlockingProgressTask.stop()`
        :rtype: ~cliasi.Cliasi.NonBlockingProgressTask
        """

        if self.__verbose_check(verbosity):
            return self.__get_null_task()

        return self.__get_progressbar_task(
            message,
            progress,
            ANIMATION_SYMBOLS_PROGRESSBAR["download"][
                randint(0, len(ANIMATION_SYMBOLS_PROGRESSBAR["download"]) - 1)
            ],
            show_percent,
            interval,
            TextColor.BRIGHT_CYAN,
            unicorn,
            override_messages_stay_in_one_line,
        )


cli: Cliasi
"""Default Cliasi instance (shows INFO and above by default)"""
cli = Cliasi("CLI", min_verbose_level=logging.INFO)
