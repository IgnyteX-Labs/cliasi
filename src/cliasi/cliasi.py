from time import sleep
from random import randint
from typing import Union, Optional, Callable
from threading import Thread, Event


from .constants import PROGRESSBAR_LOADING, LOADING, Color, DEFAULT_TERMINAL_SIZE

try:
    from os import get_terminal_size


    def _terminal_size() -> int:
        return get_terminal_size().columns

    _terminal_size()  # Try if getting terminal size works
except Exception as e:
    print("! [cliasi] Error: Could not retrieve terminal size!", e)

    def _terminal_size() -> int:
        return DEFAULT_TERMINAL_SIZE


class NonBlockingAnimationTask:
    """
    Defines a non-blocking animation task run on another Thread
    """
    message: str
    oneline_override: bool
    condition: Event
    _thread: Thread

    def __init__(self, message: str, stop: Event, oneline_override: bool) -> None:
        self.message = message
        self.oneline_override = oneline_override
        self.condition = stop

    def stop(self):
        self.condition.set()
        self._thread.join()
        if self.oneline_override:
            print("")


class NonBlockingProgressTask(NonBlockingAnimationTask):
    """
    Defines a non-blocking animation task with a progress bar run on another Thread
    """
    progress: int
    index: int = 0
    _update: Callable[[], None]  # Function that only re-renders the progress bar

    def __init__(self, message: str, stop: Event, oneline_override: bool, progress: int) -> None:
        super().__init__(message, stop, oneline_override)
        self.progress = progress

    def update(self, progress: int) -> None:
        self.progress = progress
        self._update()


class Cliasi:
    def __init__(self, prefix: str = "", use_oneline: bool = False, colors: bool = True, verbose_level: int = 0,
                 seperator: str = "|"):
        """
        Initialize a cliasi instance.
        :param prefix: Message Prefix [prefix] message
        :param use_oneline: Have all messages appear in one line by default
        :param colors: Enable color display
        :param verbose_level: Only displays messages with verbose level higher than this value
        :param seperator: Seperator between prefix and message
        """
        self.__prefix = ""
        self.update_prefix(prefix)
        self.oneline = use_oneline
        self.enable_colors = colors
        self.min_verbose_level = verbose_level
        self.prefix_seperator = seperator

    def update_prefix(self, prefix: str):
        """
        Update the message prefix of this instance.
        Prefixes should be three letters long but do as you wish.
        :param prefix: New message prefix without brackets []
        :return:
        """
        self.__prefix = Color.DIM + f"[{prefix}]"

    def __verbose_check(self, level: int) -> bool:
        """
        Check if message should be sent
        :param level: given verbosity level
        :return: False if message should be sent, true if message should not be sent
        """
        return level > self.min_verbose_level

    def __print(self, color: Color, symbol: str, message: str, oneline_override: Optional[bool]):
        """
        Print message to console
        :param color: Color to print message and symbol
        :param symbol: Symbol to print at start of message
        :param message: Message to print
        :param oneline_override: Override the message to stay in the command line
        :return:
        """
        oneline = self.oneline if oneline_override is None else oneline_override
        print('\r\x1b[2K\r',
              (color if self.enable_colors else "") + symbol,
              Color.DIM + self.__prefix + Color.RESET,
              self.prefix_seperator + (color if self.enable_colors else ""),
              message,
              end=("" if oneline else "\n") + Color.RESET,
              flush=True
              )

    def info(self, message: str, verbosity: int = 0, oneline_override: Optional[bool] = None):
        """
        Send an info message in format i [prefix] message
        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param oneline_override: Override the message to stay in the command line    
    
        :return:
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(Color.BRIGHT_BLUE, "i", message, oneline_override)

    def log(self, message: str, verbosity: int = 0, oneline_override: Optional[bool] = None):
        """
        Send a log message in format LOG [prefix] message
        :param message: Message to log
        :param verbosity: Verbosity of this message
        :param oneline_override: Override the message to stay in the command line    
        :return:
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(Color.BRIGHT_BLUE, "LOG", message, oneline_override)

    def warn(self, message: str, verbosity: int = 0, oneline_override: Optional[bool] = None):
        """
        Send a warning message in format ! [prefix] message
        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param oneline_override: Override the message to stay in the command line    
        :return:
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(Color.YELLOW, "!", message, oneline_override)

    def success(self, message: str, verbosity: int = 0, oneline_override: Optional[bool] = None):
        """
        Send a success message in format ✔ [prefix] message
        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param oneline_override: Override the message to stay in the command line    
        :return:
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(Color.GREEN, "✔", message, oneline_override)

    def fail(self, message: str, verbosity: int = 0, oneline_override: Optional[bool] = None):
        """
        Send a failure message in format X [prefix] message
        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param oneline_override: Override the message to stay in the command line    
        :return:
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(Color.RED, "X", message, oneline_override)

    def neutral(self, message: str, verbosity: int = 0, oneline_override: Optional[bool] = None):
        """
        Send a neutral message in format # [prefix] message
        :param message: Message to send
        :param verbosity: Verbosity of this message
        :param oneline_override: Override the message to stay in the command line    
        :return:
        """
        if self.__verbose_check(verbosity):
            return

        self.__print(Color.BLUE, "#", message, oneline_override)

    def ask(self, message: str, oneline_override: Optional[bool] = None) -> str:
        """
        Ask for input in format ? [prefix] message
        :param message: Question to ask
        :param oneline_override: Override the message to stay in the command line    
        :return:
        """

        self.__print(Color.MAGENTA, "?", message, oneline_override)
        result = input("")
        oneline = self.oneline if oneline_override is None else oneline_override
        if oneline:
            print('\x1b[1A\x1b[2K', end="")
        return result

    def __show_animation_frame(self, message: str, selection_symbol: int, selection_animation: int, index_total: int):
        """
        Show a single animation frame based on total index
        :param message: Message to show
        :param selection_symbol: Whoch symbol animation to show
        :param selection_animation: Which animation to show
        :param index_total: What index we are on
        :return:
        """
        self.__print(
            Color.BRIGHT_YELLOW,
            LOADING["symbol"][selection_symbol][index_total % len(LOADING["symbol"][selection_symbol])],
            LOADING["animation"][selection_animation]["frames"][
                (index_total // LOADING["animation"][selection_animation]["frame_every"]) % len(
                    LOADING["animation"][selection_animation]["frames"])] + " " + message,
            True)

    def animate_message_blocking(self,
                                 message: str,
                                 time: Union[int, float],
                                 interval: Union[int, float] = 0.25,
                                 oneline_override: Optional[bool] = None):
        """
        Display a loading animation for a fixed time
        This will block the main thread using time.sleep
        :param message: Message to display
        :param time: Time to display for
        :param interval: Interval between changes in loading animation
        :param oneline_override: Override the message to stay in the command line
        :return:
        """
        remaining = time
        selection_symbol, selection_animation = randint(0, len(LOADING["symbol"]) - 1), randint(0, len(
            LOADING["animation"]) - 1)
        index_total = 0
        while remaining > 0:
            self.__show_animation_frame(message, selection_symbol, selection_animation, index_total)
            index_total += 1

            remaining -= interval
            if remaining < interval:
                break

            sleep(interval)

        sleep(remaining)
        self.success(message, oneline_override=oneline_override)

    def __scale_progressbar_to_max(self, message: str, progress: int, show_percent: bool) -> str:
        """
        Returns a string representation of the progress bar
        Like this [====message===] xx%
        :param message: Message to display
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
        dead_space = 3 + len(self.__prefix) + len(self.prefix_seperator) + len(f" {p}%") if show_percent else 0
        # symbol(1) + space (2) + prefix + separator + space (3)

        # Clamp progress
        p = max(0, min(100, progress))

        # Determine available width for the bar content (inside the brackets)
        total_cols = _terminal_size()

        inside_width = max(8, total_cols - max(0, dead_space) - 2)

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

    def progressbar(self, message: str, progress: int = 0, oneline_override: Optional[bool] = False,
                    show_percent: bool = False):
        """
        Display a progress bar with specified progress
        This requires grabbing correct terminal width
        This is not animated. Call it multiple times to update
        :param message: Message to display
        :param progress: Progress to display
        :param oneline_override: Override the message to stay in the command line
        :param show_percent: Show percent next to the progressbar
        :return:
        """

        # Print the bar. Keep it on one line unless overridden by oneline_override.
        self.__print(Color.BRIGHT_YELLOW, "#", self.__scale_progressbar_to_max(message, progress, show_percent),
                     oneline_override)

    def progressbar_download(self, message: str, progress: int = 0, show_percent: bool = False,
                             oneline_override: Optional[bool] = False):
        """
        Display a download bar with specified progress
        This is not animated. Call it multiple times to update
        :param message: Message to display
        :param progress: Progress to display
        :param show_percent: Show percent next to the progressbar
        :param oneline_override: Override the message to stay in the command line
        :return:
        """
        self.__print(Color.CYAN, "⤓", self.__scale_progressbar_to_max(message, progress, show_percent),
                     oneline_override)

    def animate_message_non_blocking(self, message: str, interval: Union[int, float] = 0.25,
                                     oneline_override: Optional[bool] = None) -> NonBlockingAnimationTask:
        """
        Display a loading anomation in the background
        Stop animation by calling .stop() on the returned object
        :param message: Message to display
        :param interval: Interval for animation to play
        :param oneline_override: Override the message to stay in the command line
        :return:
        """
        selection_symbol, selection_animation = randint(0, len(LOADING["symbol"]) - 1), randint(0,
                                                                                                len(LOADING[
                                                                                                        "animation"]) - 1)

        condition = Event()
        task = NonBlockingAnimationTask(message, condition,
                                        oneline_override if oneline_override is not None else self.oneline)

        def animate():
            """
            Display animation
            :return:
            """
            index_total = 0
            while not condition.is_set():
                self.__show_animation_frame(task.message, selection_symbol, selection_animation, index_total)
                index_total += 1
                task.condition.wait(timeout=interval)

        thread = Thread(target=animate, args=(), daemon=True)
        task._thread = thread
        thread.start()
        return task

    def __progressbar_nonblocking(self, message: str, progress: int, type: str, show_percent: bool,
                                  interval: Union[int, float],
                                  color: Color,
                                  oneline_override: Optional[bool] = False) -> NonBlockingProgressTask:

        animation = PROGRESSBAR_LOADING[type][randint(0, len(PROGRESSBAR_LOADING[type]) - 1)]

        condition = Event()

        task = NonBlockingProgressTask(message, condition,
                                       oneline_override if oneline_override is not None else self.oneline,
                                       progress)

        def update_bar():
            """
            Update only the progressbar section of the animation.
            :return:
            """
            self.__print(color, animation[task.index % len(animation)],
                         self.__scale_progressbar_to_max(task.message, task.progress, show_percent), True)

        def animate():
            """
            Animate the progressbar
            :return:
            """
            while not condition.is_set():
                self.__print(color, animation[task.index % len(animation)],
                             self.__scale_progressbar_to_max(task.message, task.progress, show_percent), True)
                task.index += 1
                condition.wait(timeout=interval)

        thread = Thread(target=animate, args=(), daemon=True)
        task._thread = thread
        task._update = update_bar
        thread.start()
        return task

    def progressbar_animated_normal(self, message: str, progress: int = 0, interval: Union[int, float] = 0.25,
                                    show_percent: bool = False,
                                    oneline_override: Optional[bool] = False) -> NonBlockingProgressTask:
        """
        Display an animated progressbar
        Update progress using the returned Task object
        :param message: Message to display
        :param progress: Current Progress to display
        :param show_percent: Show percent next to the progressbar
        :param oneline_override: Override the message to stay in the command line
        :return: NonBlockingProgressTask on which you can call update(progress) and stop()
        """
        return self.__progressbar_nonblocking(message, progress, "default", show_percent, interval, Color.BRIGHT_YELLOW,
                                              oneline_override)

    def progressbar_animated_download(self, message: str, progress: int = 0, interval: Union[int, float] = 0.25,
                                      show_percent: bool = False,
                                      oneline_override: Optional[bool] = False) -> NonBlockingProgressTask:
        """
        Display an animated progressbar
        Update progress using the returned Task object
        :param message: Message to display
        :param progress: Current Progress to display
        :param show_percent: Show percent next to the progressbar
        :param oneline_override: Override the message to stay in the command line
        :return: NonBlockingProgressTask on which you can call update(progress) and stop()
        """
        return self.__progressbar_nonblocking(message, progress, "download", show_percent, interval, Color.CYAN,
                                              oneline_override)
