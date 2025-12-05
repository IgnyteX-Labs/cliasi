import logging
import sys
import textwrap
from time import sleep
from random import randint
from getpass import getpass
from typing import Union, Optional, Callable, List, Dict, TextIO
from threading import Thread, Event, Lock

from .constants import ANIMATION_SYMBOLS_PROGRESSBAR, ANIMATIONS_MAIN, ANIMATIONS_SYMBOLS, TextColor, \
    DEFAULT_TERMINAL_SIZE, UNICORN

_print_lock: Lock = Lock()

STDOUT_STREAM: TextIO = sys.stdout
STDERR_STREAM: TextIO = sys.stderr

# Try to get the terminal size
try:
    from os import get_terminal_size


    def _terminal_size() -> int:
        return get_terminal_size().columns


    _terminal_size()  # Try if getting terminal size works

except Exception as e:
    print("! [cliasi] Error: Could not retrieve terminal size!", e)


    def _terminal_size() -> int:
        return DEFAULT_TERMINAL_SIZE


class Cliasi:
    """Cliasi CLI instance. Stores display settings and a minimum verbosity threshold.

    Verbosity model:
      - Uses Python logging numeric levels as the verbosity scale (e.g. DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50).
      - A message will be printed when message_verbosity >= min_verbose_level (same semantics as logging.Logger.setLevel).
        Example: if min_verbose_level == logging.INFO (20), messages with verbosity logging.INFO (20), WARNING (30),
        ERROR (40), CRITICAL (50) will be shown; DEBUG (10) will be suppressed.
    """
    min_verbose_level: int
    messages_stay_in_one_line: bool
    enable_colors: bool
    __prefix_seperator: str
    __space_before_message: int  # Number of spaces before message start (for alignment)

    def __init__(self, prefix: str = "", messages_stay_in_one_line: bool = False, colors: bool = True,
                 min_verbose_level: Optional[int] = None,
                 seperator: str = "|"):
        """
        Initialize a cliasi instance.

        :param prefix: Message Prefix [prefix] message
        :param messages_stay_in_one_line: Have all messages appear in one line by default
        :param colors: Enable color display
        :param min_verbose_level: Only displays messages with verbose level higher than this value (default is logging.INFO),
        None will result in the verbosity level getting set to the value of the global instance which is by default 0
        :param seperator: Seperator between prefix and message
        """
        self.__prefix = ""
        self.messages_stay_in_one_line = messages_stay_in_one_line
        self.enable_colors = colors
        self.min_verbose_level = min_verbose_level if min_verbose_level is not None else cli.min_verbose_level
        self.__prefix_seperator = seperator
        self.set_prefix(prefix)

    def __compute_space_before_message(self) -> None:
        """
        Compute empty space before message for alignment WITHOUT symbol!

        :return: None
        """
        # symbol + space (1) + prefix + space(2) + separator + space (3) -> message
        self.__space_before_message = 3 + len(self.__prefix) + len(self.__prefix_seperator)

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

    def __print(self, color: TextColor, symbol: str, message: str, override_messages_stay_in_one_line: Optional[bool],
                color_message: bool = True, write_to_stderr: bool = False) -> None:
        """
        Print message to console with word wrapping and customizable separators.

        :param color: Color to print message and symbol
        :param symbol: Symbol to print at start of message
        :param message: Message to print
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :param color_message: Print the main message with color
        :param write_to_stderr: Write message to stderr instead of stdout
        :return: None
        """
        oneline = self.messages_stay_in_one_line if override_messages_stay_in_one_line is None else override_messages_stay_in_one_line
        content_space = _terminal_size() - (self.__space_before_message + len(symbol) + 1)  # Space left for content per line
        # space(1) + symbol + space_before_message (prefix + seperator) -> message

        lines = []

        for paragraph in message.splitlines():
            wrapped = textwrap.wrap(paragraph, width=content_space)
            if wrapped:
                lines.extend(wrapped)
            else:
                lines.append("")

        with _print_lock:
            index = 0
            for line in lines:
                index += 1
                if index == 1:
                    print('\r\x1b[2K\r',
                          (color if self.enable_colors else "") + symbol,
                          TextColor.DIM + self.__prefix + TextColor.RESET,
                          self.__prefix_seperator + (color if self.enable_colors and color_message else ""),
                          line,
                          file=STDERR_STREAM if write_to_stderr else STDOUT_STREAM,
                          end=("" if oneline and len(lines) != 1 else "\n") + TextColor.RESET,
                          flush=True
                          )
                else:
                    print('\r\x1b[2K\r',
                          # space (done because new argument) + symbol + space (1) + prefix + space (not done because new argument)
                          " " * (len(self.__prefix) + len(symbol) + 1),
                          self.__prefix_seperator,
                          (color if self.enable_colors and color_message else "") + line,
                          file=STDERR_STREAM if write_to_stderr else STDOUT_STREAM,
                          end="\n" + TextColor.RESET,
                          flush=True
                          )

    def message(self, message: str, verbosity: int = logging.INFO,
                override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Send a message in format # [prefix] message

        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.WHITE + TextColor.DIM, "#", message, override_messages_stay_in_one_line,
                     color_message=False)

    def info(self, message: str, verbosity: int = logging.INFO,
             override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Print an informational message.
        Send an info message in format i [prefix] message

        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.BRIGHT_WHITE, "i", message, override_messages_stay_in_one_line, color_message=False)

    def log(self, message: str, verbosity: int = logging.DEBUG,
            override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Send a log message in format LOG [prefix] message

        :param message: Message to log
        :param verbosity: Verbosity of this message
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.WHITE + TextColor.DIM, "LOG", message, override_messages_stay_in_one_line,
                     color_message=False)

    def log_small(self, message: str, verbosity: int = logging.DEBUG,
                  override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Send a log message in format LOG [prefix] message

        :param message: Message to log
        :param verbosity: Verbosity of this message
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.WHITE + TextColor.DIM, "L", message, override_messages_stay_in_one_line,
                     color_message=False)

    def list(self, message: str, verbosity: int = logging.INFO,
             override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Send a list style message in format * [prefix] message

        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.BRIGHT_WHITE, "-", message, override_messages_stay_in_one_line, color_message=False)

    def warn(self, message: str, verbosity: int = logging.WARNING,
             override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Send a warning message in format ! [prefix] message

        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.BRIGHT_YELLOW, "!", message, override_messages_stay_in_one_line)

    def fail(self, message: str, verbosity: int = logging.CRITICAL,
             override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Send a failure message in format X [prefix] message

        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.BRIGHT_RED, "X", message, override_messages_stay_in_one_line, write_to_stderr=True)

    def success(self, message: str, verbosity: int = logging.INFO,
                override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Send a success message in format ✔ [prefix] message

        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.BRIGHT_GREEN, "✔", message, override_messages_stay_in_one_line)

    @staticmethod
    def newline() -> None:
        """
        Print a newline.

        :return: None
        """
        print("", file=STDOUT_STREAM, flush=True)

    def ask(self, message: str, hide_input: bool = False,
            override_messages_stay_in_one_line: Optional[bool] = None) -> str:
        """
        Ask for input in format ? [prefix] message

        :param message: Question to ask
        :param hide_input: True hides user input
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: The user input as a string.
        """

        self.__print(TextColor.BRIGHT_MAGENTA if hide_input else TextColor.MAGENTA, "?", message, True)
        if hide_input:
            result = getpass("")
        else:
            result = input("")
        oneline = self.messages_stay_in_one_line if override_messages_stay_in_one_line is None else override_messages_stay_in_one_line
        if oneline:
            print('\x1b[1A\x1b[2K', end="")
        return result

    def __show_animation_frame(self, message: str, color: TextColor, current_symbol_frame: str,
                               current_animation_frame: str) -> None:
        """
        Show a single animation frame based on total index

        :param message: Message to show
        :param color: Color of message
        :param current_symbol_frame: Current symbol animation to show
        :param current_animation_frame: Current animation frame to show
        :return: None
        """
        self.__print(
            color,
            current_symbol_frame,
            current_animation_frame + ("" if current_animation_frame == "" else " ") + message,
            True)

    def animate_message_blocking(self,
                                 message: str,
                                 time: Union[int, float],
                                 verbosity: int = logging.INFO,
                                 interval: Union[int, float] = 0.25,
                                 unicorn: bool = False,
                                 override_messages_stay_in_one_line: Optional[bool] = None) -> None:
        """
        Display a loading animation for a fixed time
        This will block the main thread using time.sleep

        :param message: Message to display
        :param time: Time to display for
        :param verbosity: Verbosity of this message
        :param interval: Interval between changes in loading animation
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """

        if self.__verbose_check(verbosity):
            return

        remaining = time
        selection_symbol, selection_animation = randint(0, len(ANIMATIONS_SYMBOLS) - 1), randint(0, len(
            ANIMATIONS_MAIN) - 1)
        symbol_frames, animation_frames = ANIMATIONS_SYMBOLS[selection_symbol], ANIMATIONS_MAIN[selection_animation][
            "frames"]
        index_total = 0
        while remaining > 0:
            self.__show_animation_frame(message,
                                        TextColor.BRIGHT_MAGENTA if not unicorn else UNICORN[
                                            index_total % len(UNICORN)],
                                        symbol_frames[index_total % len(symbol_frames)],
                                        animation_frames[
                                            (index_total // ANIMATIONS_MAIN[selection_animation]["frame_every"]) % len(
                                                animation_frames)])
            index_total += 1

            remaining -= interval
            if remaining < interval:
                break

            sleep(interval)

        sleep(remaining)
        if not (
                self.messages_stay_in_one_line if override_messages_stay_in_one_line is not None else override_messages_stay_in_one_line):
            print("")

    def __format_progressbar_to_screen_width(self, message: str, symbol: str, progress: int, show_percent: bool) -> str:
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
        # Estimate the characters printed beColor the bar by __print: symbol + space + " [prefix] " + space + separator
        # We don't know the visual width of color codes; ignore them as they don't take columns.
        # Use a conservative estimate with a typical 1-char symbol (we'll use '#').
        dead_space = 1 + len(symbol) + self.__space_before_message + (len(f" {p}%") if show_percent else 0)
        # space(1) + symbol + space_before_message (prefix + seperator) -> message (+ space + percent if needed)

        # Clamp progress
        p = max(0, min(100, progress))

        # Determine available width for the bar content (inside the brackets)
        total_cols = _terminal_size()

        inside_width = max(8, total_cols - max(0, dead_space) - 2)

        # Prepare message to fit, centered, without overlapping percent area
        # Compute the maximum width available for message without touching percent area on the far right
        max_message_width = max(0, inside_width)
        msg = message if message is not None else ""
        if len(msg) > max_message_width:
            # Truncate with ellipsis if possible
            if max_message_width >= 3:
                msg = msg[: max_message_width - 1] + "…"
            else:
                msg = msg[:max_message_width]
        M = len(msg)

        # Determine message start so that it is centered within the space that excludes the percent area on the far right
        # We consider the layout as: [ left | message | middle | percent | right(end) ] where percent is fixed at the end
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
        filled = 0
        i = 0
        while filled < target_fill and i < inside_width:
            # Skip positions occupied by message
            if msg_start <= i < msg_end:
                i += 1
                continue
            bar[i] = "="
            filled += 1
            i += 1

        # Wrap with brackets
        return "[" + "".join(bar) + "]" + (f" {p}%" if show_percent else "")

    def progressbar(self, message: str, verbosity: int = logging.INFO, progress: int = 0,
                    override_messages_stay_in_one_line: Optional[bool] = False,
                    show_percent: bool = False) -> None:
        """
        Display a progress bar with specified progress
        This requires grabbing correct terminal width
        This is not animated. Call it multiple times to update

        :param message: Message to display
        :param verbosity: Verbosity to display
        :param progress: Progress to display
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :param show_percent: Show percent next to the progressbar
        :return: None
        """

        if self.__verbose_check(verbosity):
            return

            # Print the bar. Keep it on one line unless overridden by override_messages_stay_in_one_line.
        self.__print(TextColor.BLUE, "#",
                     self.__format_progressbar_to_screen_width(message, "#", progress, show_percent),
                     override_messages_stay_in_one_line)

    def progressbar_download(self, message: str, verbosity: int = logging.INFO, progress: int = 0,
                             show_percent: bool = False,
                             override_messages_stay_in_one_line: Optional[bool] = False) -> None:
        """
        Display a download bar with specified progress
        This is not animated. Call it multiple times to update

        :param message: Message to display
        :param verbosity: Verbosity to display
        :param progress: Progress to display
        :param show_percent: Show percent next to the progressbar
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: None
        """

        if self.__verbose_check(verbosity):
            return

        self.__print(TextColor.BRIGHT_CYAN, "⤓",
                     self.__format_progressbar_to_screen_width(message, "⤓", progress, show_percent),
                     override_messages_stay_in_one_line)

    class NonBlockingAnimationTask:
        """
        Defines a non-blocking animation task run on another Thread
        """
        _message_stays_in_one_line: bool
        _condition: Event
        _message: str  # Current message to display
        _index: int = 0  # Animation frame total index
        _thread: Thread
        _update: Callable[[], None]  # Update call to update with current animation frame

        def __init__(self, message: str, stop_condition: Event, message_stays_in_one_line: bool) -> None:
            self._message = message
            self._message_stays_in_one_line = message_stays_in_one_line
            self._condition = stop_condition

        def stop(self):
            self._condition.set()
            self._thread.join()
            if not self._message_stays_in_one_line:
                print("")

        def update(self, message: Optional[str] = None) -> None:
            """
            Update message of animation

            :param message: Message to update to (None for no update)
            :return: None
            """
            self._message = message if message is not None else self._message
            self._update()

    def __get_animation_task(self, message: str, color: TextColor, symbol_animation: List[str],
                             main_animation: Dict[str, Union[int, List[str]]], interval: Union[int, float],
                             unicorn: bool = False,
                             override_messages_stay_in_one_line: Optional[bool] = False) -> NonBlockingAnimationTask:
        """
        Create an animation task

        :param message: Message to display
        :param color: Color of message
        :param symbol_animation: The symbol animation to display as string frames in a list
        :param main_animation: The main animation to display as string frames in a list
        :param interval: The interval to display as string frames in a list
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line: Override message to stay in one line
        :return A NonBlockingAnimationTask
        """
        condition = Event()

        task = Cliasi.NonBlockingAnimationTask(message, condition,
                                               override_messages_stay_in_one_line if override_messages_stay_in_one_line is not None else self.messages_stay_in_one_line)

        def update() -> None:
            """
            Update the animation to the current frame

            :return: None
            """
            self.__show_animation_frame(task._message, color if not unicorn else UNICORN[task._index % len(UNICORN)],
                                        symbol_animation[task._index % len(symbol_animation)],
                                        main_animation["frames"][(task._index // main_animation["frame_every"]) % len(
                                            main_animation["frames"])])

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

    def animate_message_non_blocking(self, message: str, verbosity: int = logging.INFO,
                                     interval: Union[int, float] = 0.25,
                                     unicorn: bool = False,
                                     override_messages_stay_in_one_line: Optional[
                                         bool] = None) -> Optional[NonBlockingAnimationTask]:
        """
        Display a loading animation in the background
        Stop animation by calling .stop() on the returned object

        :param message: Message to display
        :param verbosity: Verbosity of message
        :param interval: Interval for animation to play
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: NonBlockingAnimationTask if verbosity requirement is met.
        """

        if self.__verbose_check(verbosity):
            return self.__get_null_task()

        selection_symbol, selection_animation = randint(0, len(ANIMATIONS_SYMBOLS) - 1), randint(0,
                                                                                                 len(ANIMATIONS_MAIN) - 1)
        return self.__get_animation_task(message, TextColor.BRIGHT_MAGENTA, ANIMATIONS_SYMBOLS[selection_symbol],
                                         ANIMATIONS_MAIN[selection_animation], interval, unicorn,
                                         override_messages_stay_in_one_line)

    def animate_message_download_non_blocking(self, message: str, verbosity: int = logging.INFO,
                                              interval: Union[int, float] = 0.25, unicorn: bool = False,
                                              override_messages_stay_in_one_line: Optional[
                                                  bool] = False) -> Optional[NonBlockingAnimationTask]:
        """
        Display a downloading animation in the background

        :param message: Message to display
        :param verbosity: Verbosity of message
        :param interval: Interval for animation to play
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: A NonBlockingAnimationTask if verbosity requirement is met.
        """

        if self.__verbose_check(verbosity):
            return self.__get_null_task()

        selection_animation = randint(0, len(ANIMATIONS_MAIN) - 1)
        return self.__get_animation_task(message, TextColor.BRIGHT_CYAN,
                                         ANIMATION_SYMBOLS_PROGRESSBAR["download"][
                                             randint(0, len(ANIMATION_SYMBOLS_PROGRESSBAR["download"]) - 1)],
                                         ANIMATIONS_MAIN[selection_animation],
                                         interval,
                                         unicorn,
                                         override_messages_stay_in_one_line)

    class NonBlockingProgressTask(NonBlockingAnimationTask):
        """
        Defines a non-blocking animation task with a progress bar run on another Thread
        """
        _progress: int

        def __init__(self, message: str, stop_condition: Event, override_messages_stay_in_one_line: bool,
                     progress: int) -> None:
            super().__init__(message, stop_condition, override_messages_stay_in_one_line)
            self._progress = progress

        def update(self, message: Optional[str] = None, progress: Optional[int] = None, *args, **kwargs) -> None:
            """
            Update progressbar message and progress

            :param message: Message to update to (None for no update)
            :param progress: Progress to update to (None for no update)
            :return: None
            """
            self._progress = progress if progress is not None else self._progress
            super(Cliasi.NonBlockingProgressTask, self).update(message)

    def __get_null_task(self) -> NonBlockingProgressTask:
        """
        Get a null progressbar task to return when verbosity is not met to not return None

        :return: "fake" NonBlockingProgressTask
        """
        task = Cliasi.NonBlockingProgressTask("", Event(), False, 0)
        task._update = lambda: None
        task.stop = lambda: None
        return task

    def __get_progressbar_task(self, message: str, progress: int, symbol_animation: List[str], show_percent: bool,
                               interval: Union[int, float],
                               color: TextColor,
                               unicorn: bool = False,
                               override_messages_stay_in_one_line: Optional[
                                   bool] = False) -> NonBlockingProgressTask:
        """
        Get a progressbar task

        :param message: Message to display
        :param progress: Initial progress
        :param symbol_animation: List of string for symbol animation
        :param show_percent: Show percent at end of progressbar
        :param interval: Interval for animation to play
        :param color: Color of progressbar
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: NonBlockingProgressTask
        """

        condition = Event()

        task = Cliasi.NonBlockingProgressTask(message, condition,
                                              override_messages_stay_in_one_line if override_messages_stay_in_one_line is not None else self.messages_stay_in_one_line,
                                              progress)

        def update_bar() -> None:
            """
            Update only the progressbar section of the animation.

            :return: None
            """
            current_symbol = symbol_animation[task._index % len(symbol_animation)]
            self.__show_animation_frame(
                self.__format_progressbar_to_screen_width(message, current_symbol, task._progress, show_percent),
                color if not unicorn else UNICORN[task._index % len(UNICORN)],
                current_symbol, current_animation_frame="")

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

    def progressbar_animated_normal(self, message: str,
                                    verbosity: int = logging.INFO,
                                    progress: int = 0,
                                    interval: Union[int, float] = 0.25,
                                    show_percent: bool = False,
                                    unicorn: bool = False,
                                    override_messages_stay_in_one_line: Optional[
                                        bool] = False) -> NonBlockingProgressTask:
        """
        Display an animated progressbar
        Update progress using the returned Task object

        :param message: Message to display
        :param verbosity: Verbosity of message
        :param interval: Interval between animation frames
        :param progress: Current Progress to display
        :param show_percent: Show percent next to the progressbar
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: NonBlockingProgressTask on which you can call update(progress) and stop()
        """

        if self.__verbose_check(verbosity):
            return self.__get_null_task()

        return self.__get_progressbar_task(message,
                                           progress,
                                           ANIMATION_SYMBOLS_PROGRESSBAR["default"][
                                               randint(0, len(ANIMATION_SYMBOLS_PROGRESSBAR["default"]) - 1)],
                                           show_percent,
                                           interval,
                                           TextColor.BLUE,
                                           unicorn,
                                           override_messages_stay_in_one_line)

    def progressbar_animated_download(self, message: str,
                                      verbosity: int = logging.INFO,
                                      progress: int = 0,
                                      interval: Union[int, float] = 0.25,
                                      show_percent: bool = False,
                                      unicorn: bool = False,
                                      override_messages_stay_in_one_line: Optional[
                                          bool] = False) -> NonBlockingProgressTask:
        """
        Display an animated progressbar
        Update progress using the returned Task object

        :param message: Message to display
        :param verbosity: Verbosity of message
        :param interval: Interval between animation frames
        :param progress: Current Progress to display
        :param show_percent: Show percent next to the progressbar
        :param unicorn: Enable unicorn mode
        :param override_messages_stay_in_one_line: Override the message to stay in one line
        :return: NonBlockingProgressTask on which you can call update(progress) and stop()
        """

        if self.__verbose_check(verbosity):
            return self.__get_null_task()

        return self.__get_progressbar_task(message,
                                           progress,
                                           ANIMATION_SYMBOLS_PROGRESSBAR["download"][
                                               randint(0, len(ANIMATION_SYMBOLS_PROGRESSBAR["download"]) - 1)],
                                           show_percent,
                                           interval,
                                           TextColor.BRIGHT_CYAN,
                                           unicorn,
                                           override_messages_stay_in_one_line)


cli = Cliasi("CLI", min_verbose_level=logging.INFO)
# Default Cliasi instance (shows INFO and above)
