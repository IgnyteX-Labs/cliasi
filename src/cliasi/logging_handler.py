"""
Logging handler for cliasi.

This module provides a custom logging handler that integrates with the Cliasi instance.
"""

import logging
import sys
import traceback

from . import STDERR_STREAM
from .cliasi import Cliasi


class CLILoggingHandler(logging.Handler):
    """
    Logging handler that forwards records to the cliasi.cli Cliasi instance
    """
    cli: Cliasi

    def __init__(self, cli_instance: Cliasi):
        """
        Initialize the logging handler with a Cliasi instance

        :param cli_instance: Cliasi instance (default cli instance)
        """
        super().__init__()
        self.cli = cli_instance
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to the Cliasi instance

        :param record: logging.LogRecord
        :return: None
        """
        try:
            msg = self.format(record)
            level = record.levelno
            if level >= logging.ERROR:
                exc_text = ""
                if record.exc_info:
                    # Unpack exc_info tuple explicitly to satisfy static analysis and clarity
                    exc_type, exc_value, exc_tb = record.exc_info
                    exc_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
                # pass verbosity so Cliasi can filter
                self.cli.fail(msg + exc_text, verbosity=level)
            elif level >= logging.WARNING:
                self.cli.warn(msg, verbosity=level)
            elif level >= logging.INFO:
                self.cli.info(msg, verbosity=level)
            else:
                self.cli.log_small(msg, verbosity=level)
        except Exception:
            STDERR_STREAM.write("! [cliasi] Failed to emit log record\n")
            STDERR_STREAM.write(traceback.format_exc() + "\n")


def install_logger(cli_instance: Cliasi, replace_root_handlers: bool = False) -> None:
    """
    Install the CLILoggingHandler to the root logger

    :param cli_instance: Cliasi instance (default cli instance)
    :param replace_root_handlers: If True, existing StreamHandlers will be removed from the root logger so that only cliasi will print to the console. If False, existing StreamHandlers are left unchanged.
    :return: None
    """
    handler = CLILoggingHandler(cli_instance)

    root = logging.getLogger()
    for h in list(root.handlers):
        if isinstance(h, logging.StreamHandler):
            root.removeHandler(h)

    if replace_root_handlers:
        for h in list(root.handlers):
            if isinstance(h, logging.StreamHandler):
                root.removeHandler(h)

    root.addHandler(handler)
    root.setLevel(logging.NOTSET)


def install_exception_hook(cli_instance: Cliasi) -> None:
    """
    Install a global exception hook that logs uncaught exceptions to the Cliasi instance

    :param cli_instance: Cliasi instance (default cli instance)
    """

    def handle_exception(exc_type, exc_value, exc_traceback):
        # Preserve KeyboardInterrupt behavior
        try:
            if isinstance(exc_type, type) and issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
        except Exception:
            # If exc_type is malformed for issubclass, continue to treat it as a non-KeyboardInterrupt
            pass

        # Detect whether the exception originated from the cliasi package to avoid recursive failures
        tb = exc_traceback
        from_cliasi = False
        while tb is not None:
            frame = tb.tb_frame
            module_name = frame.f_globals.get("__name__", "")
            filename = frame.f_code.co_filename if hasattr(frame.f_code, 'co_filename') else ""
            if module_name.startswith("cliasi") or ("/cliasi/" in filename) or ("\\cliasi\\" in filename) or filename.endswith("cliasi.py"):
                from_cliasi = True
                break
            tb = tb.tb_next

        if from_cliasi:
            # Avoid calling cli_instance.fail (which may itself raise). Write a minimal message to stderr.
            try:
                STDERR_STREAM.write("! [cliasi] Uncaught exception inside cliasi package; falling back to stderr\n")
                STDERR_STREAM.write("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            except Exception:
                # Last-resort fallback: print nothing else to avoid raising inside the exception hook
                pass
            return

        # Normal path: use the Cliasi instance to report the exception, but guard against any errors
        try:
            cli_instance.fail("Uncaught exception:", verbosity=logging.ERROR, override_messages_stay_in_one_line=False)
            exception_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            cli_instance.fail(exception_text, verbosity=logging.ERROR, override_messages_stay_in_one_line=False)
        except Exception:
            # If Cliasi methods fail while handling the exception, fallback to stderr so we don't raise again
            try:
                STDERR_STREAM.write("! [cliasi] Failed while reporting uncaught exception via Cliasi; writing to stderr\n")
                STDERR_STREAM.write("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            except Exception:
                # Swallow any errors from fallback reporting to avoid infinite loops
                pass

    sys.excepthook = handle_exception
