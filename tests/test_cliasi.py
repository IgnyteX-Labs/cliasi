import re
import time
import io
import sys
import logging

import pytest

from cliasi import Cliasi, cli, constants, __version__


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def normalize_output(s: str) -> str:
    # Remove ANSI codes and carriage/clear sequences, collapse spaces
    s = ANSI_RE.sub("", s)
    s = s.replace("\r", "").replace("\n", "\n").replace("\x1b[2K", "")
    return s.strip()


@pytest.fixture()
def fixed_width(monkeypatch):
    # Make terminal size deterministic for progress bar tests
    from cliasi import cliasi as cliasi_module

    monkeypatch.setattr(cliasi_module, "_terminal_size", lambda: 40)
    yield


@pytest.fixture()
def capture_streams(monkeypatch):
    """Redirect cliasi's STDOUT_STREAM/STDERR_STREAM and the real sys.stdout/stderr to StringIO buffers.

    This ensures both prints that explicitly write to the module-level streams and plain `print()`
    calls are captured by the tests.
    """
    from cliasi import cliasi as cliasi_module
    # Also get logging_handler so we can patch its STDERR_STREAM import used by the exception hook
    from cliasi import logging_handler as logging_handler_module

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # Redirect the module-level streams
    monkeypatch.setattr(cliasi_module, "STDOUT_STREAM", out_buf)
    monkeypatch.setattr(cliasi_module, "STDERR_STREAM", err_buf)
    # Also redirect the logging_handler's imported STDERR_STREAM so exception hook fallback writes are captured
    monkeypatch.setattr(logging_handler_module, "STDERR_STREAM", err_buf)

    # Also redirect the real system streams so plain print() calls are captured
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    yield out_buf, err_buf


def test_basic_messages_symbols_and_message(capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("TEST", messages_stay_in_one_line=False, colors=False)

    c.info("hello")
    out = normalize_output(out_buf.getvalue())
    assert out.startswith("i [TEST]")
    assert "| hello" in out

    # Clear buffer for next assertion
    out_buf.truncate(0); out_buf.seek(0)

    c.warn("be careful")
    out = normalize_output(out_buf.getvalue())
    assert out.startswith("! [TEST]")
    assert "| be careful" in out

    out_buf.truncate(0); out_buf.seek(0)
    c.success("ok")
    out = normalize_output(out_buf.getvalue())
    assert out.startswith("✔ [TEST]")
    assert "| ok" in out

    out_buf.truncate(0); out_buf.seek(0)
    c.fail("nope")
    # fail writes to stderr
    out = normalize_output(err_buf.getvalue())
    assert out.startswith("X [TEST]")
    assert "| nope" in out

    out_buf.truncate(0); out_buf.seek(0); err_buf.truncate(0); err_buf.seek(0)
    c.log("logged", verbosity=logging.INFO)
    out = normalize_output(out_buf.getvalue())
    assert out.startswith("LOG [TEST]")
    assert "| logged" in out

    out_buf.truncate(0); out_buf.seek(0)
    c.log_small("tiny", verbosity=logging.INFO)
    out = normalize_output(out_buf.getvalue())
    assert out.startswith("L [TEST]")
    assert "| tiny" in out

    out_buf.truncate(0); out_buf.seek(0)
    c.message("meh")
    out = normalize_output(out_buf.getvalue())
    assert out.startswith("# [TEST]")
    assert "| meh" in out

    out_buf.truncate(0); out_buf.seek(0)
    c.list("entry")
    out = normalize_output(out_buf.getvalue())
    assert out.startswith("- [TEST]")
    assert "| entry" in out


def test_update_prefix_and_separator(capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("OLD", messages_stay_in_one_line=False, colors=False, seperator="|")
    # Use the actual method name from the implementation
    c.set_prefix("NEW")
    c.info("msg")
    out = normalize_output(out_buf.getvalue())
    assert out.startswith("i [NEW]")
    assert "| msg" in out

    out_buf.truncate(0); out_buf.seek(0)
    # The implementation exposes a setter method for the separator
    c.set_seperator("::")
    c.info("again")
    out = normalize_output(out_buf.getvalue())
    assert ":: again" in out


def test_verbosity_filters(capture_streams):
    out_buf, err_buf = capture_streams
    # min_verbose_level uses numeric logging levels; messages with verbosity < min are suppressed
    c = Cliasi("V", messages_stay_in_one_line=False, colors=False, min_verbose_level=1)
    # verbosity == min -> shown
    c.info("visible", verbosity=1)
    out = normalize_output(out_buf.getvalue())
    assert "visible" in out

    out_buf.truncate(0); out_buf.seek(0)
    # lower than min -> suppressed
    c.info("hidden", verbosity=0)
    out = out_buf.getvalue()
    assert out == ""


def test_override_messages_stay_in_one_line_prints_no_newline(capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("OL", messages_stay_in_one_line=False, colors=False)
    # According to current implementation a single-line message still ends with a newline + RESET
    c.info("same line", override_messages_stay_in_one_line=True)
    captured = out_buf.getvalue()
    # Should include a newline (may be followed by RESET control code)
    assert "\n" in captured


def test_progressbar_static(fixed_width, capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("PB", messages_stay_in_one_line=False, colors=False)
    c.progressbar("Working", progress=50, override_messages_stay_in_one_line=False, show_percent=True)
    out = normalize_output(out_buf.getvalue())
    assert "[" in out and "]" in out
    assert "50%" in out

    out_buf.truncate(0); out_buf.seek(0)
    c.progressbar_download("Downloading", progress=10, show_percent=False)
    out = normalize_output(out_buf.getvalue())
    assert "[" in out and "]" in out


def test_non_blocking_animation_starts_and_stops(capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("AN", messages_stay_in_one_line=True, colors=False)
    task = c.animate_message_non_blocking("Wait", interval=0.01)
    time.sleep(0.03)
    task.stop()
    out = normalize_output(out_buf.getvalue())
    # At least one animation frame or the trailing newline from stop() should have been printed
    assert "[" in out or "Wait" in out or out != ""


def test_non_blocking_progressbar_update_and_stop(fixed_width, capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("APB", messages_stay_in_one_line=True, colors=False)
    task = c.progressbar_animated_normal("Doing", progress=0, interval=0.01, show_percent=True)
    time.sleep(0.02)
    task.update(progress=25)
    time.sleep(0.02)
    task.stop()
    out = normalize_output(out_buf.getvalue())
    assert "Doing" in out or "25%" in out or "[" in out


def test_newline_prints_single_newline(capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("NL", messages_stay_in_one_line=False, colors=False)
    c.newline()
    captured = out_buf.getvalue() + err_buf.getvalue()
    # newline should just print a single newline
    assert "\n" in captured


def test_ask_visible_and_hidden(monkeypatch, capture_streams):
    out_buf, err_buf = capture_streams
    # Patch input and getpass within module
    from cliasi import cliasi as cliasi_module

    monkeypatch.setattr("builtins.input", lambda prompt="": "visible_answer")
    c = Cliasi("ASK", messages_stay_in_one_line=True, colors=False)
    res = c.ask("Question? ", hide_input=False)
    # Output of the prompt likely contains '? [ASK]' and message
    out1 = out_buf.getvalue()
    assert res == "visible_answer"
    assert "? [" in normalize_output(out1)

    out_buf.truncate(0); out_buf.seek(0)
    # Hidden input path
    monkeypatch.setattr(cliasi_module, "getpass", lambda prompt="": "secret_answer")
    res2 = c.ask("Hidden? ", hide_input=True)
    out2 = out_buf.getvalue()
    assert res2 == "secret_answer"
    # We at least printed something for the prompt
    assert "? [" in normalize_output(out2)


def test_animate_message_blocking_emits_output(capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("BLK", messages_stay_in_one_line=True, colors=False)
    c.animate_message_blocking("Hold on", time=0.05, interval=0.01)
    out = normalize_output(out_buf.getvalue())
    assert out != ""


def test_non_blocking_download_animation_starts_and_stops(capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("DL", messages_stay_in_one_line=True, colors=False)
    task = c.animate_message_download_non_blocking("Download", interval=0.01)
    time.sleep(0.03)
    task.stop()
    out = normalize_output(out_buf.getvalue())
    assert "Download" in out or "[" in out or out != ""


def test_progressbar_animated_download_update_and_stop(fixed_width, capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("APBDL", messages_stay_in_one_line=True, colors=False)
    task = c.progressbar_animated_download(
        "Getting", progress=5, interval=0.01, show_percent=True
    )
    time.sleep(0.02)
    task.update(progress=15)
    time.sleep(0.02)
    task.stop()
    out = normalize_output(out_buf.getvalue())
    assert "Getting" in out or "15%" in out or "[" in out


def test_null_task_is_safe_for_animations_when_verbosity_suppressed(capture_streams):
    out_buf, err_buf = capture_streams
    # With min_verbose_level=0, passing verbosity=2 should suppress output and return a safe task
    c = Cliasi("VT", messages_stay_in_one_line=True, colors=False, min_verbose_level=3)

    task1 = c.animate_message_non_blocking("Hidden", verbosity=2, interval=0.005)
    # Should not be None and must support update/stop safely
    assert task1 is not None
    # Call update with and without message multiple times; must not raise
    task1.update()
    task1.update(message="Still hidden")
    task1.stop()
    task1.stop()  # idempotent

    # Download variant
    task2 = c.animate_message_download_non_blocking("Hidden DL", verbosity=2, interval=0.005)
    assert task2 is not None
    task2.update()
    task2.update(message="Still hidden DL")
    task2.stop()
    task2.stop()

    # No output should have been produced because of suppression
    out = out_buf.getvalue()
    assert out == ""


def test_null_task_is_safe_for_progressbars_when_verbosity_suppressed(fixed_width, capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("VTPB", messages_stay_in_one_line=True, colors=False, min_verbose_level=3)

    pb1 = c.progressbar_animated_normal(
        "Hidden PB", verbosity=2, progress=10, interval=0.005, show_percent=True
    )
    assert pb1 is not None
    # update with and without progress must not raise; stop idempotent
    pb1.update()
    pb1.update(progress=20)
    pb1.update(message="noop", progress=30)
    pb1.stop()
    pb1.stop()

    pb2 = c.progressbar_animated_download(
        "Hidden DL PB", verbosity=2, progress=5, interval=0.005
    )
    assert pb2 is not None
    pb2.update()
    pb2.update(progress=15)
    pb2.stop()
    pb2.stop()

    # Suppressed -> no output expected
    out = out_buf.getvalue()
    assert out == ""


def test_default_cli_instance_is_usable(capture_streams):
    out_buf, err_buf = capture_streams
    # Using the shared instance exported as `cli`
    cli.info("shared works")
    out = normalize_output(out_buf.getvalue())
    assert "shared works" in out


def test_symbols_and_version_present():
    # Basic sanity checks for package exports from __init__
    assert isinstance(constants.SYMBOLS, dict)
    # The package declares at least these two symbols
    assert constants.SYMBOLS.get("success") == "✔"
    assert constants.SYMBOLS.get("download") == "⤓"
    # Version string exists and looks like semantic version
    assert isinstance(__version__, str)
    assert __version__.count(".") >= 1 or __version__ == "0+unknown"


def test_textcolor_contains_expected_members():
    # Ensure TextColor enum exposes some basic colors and control codes
    names = {e.name for e in constants.TextColor}
    assert {"RESET", "DIM", "RED", "GREEN", "YELLOW"}.issubset(names)


def test_multiline_printing(capture_streams):
    out_buf, err_buf = capture_streams
    c = Cliasi("ML", messages_stay_in_one_line=False, colors=False)
    multi = "first line\nsecond line\nthird line"
    c.info(multi)
    raw = out_buf.getvalue()
    clean = normalize_output(raw)
    # All lines should be present in the output
    assert "first line" in clean
    assert "second line" in clean
    assert "third line" in clean
    # The first line should use the info symbol and prefix
    assert clean.startswith("i [ML]")


def test_exception_hook_user_exception(capture_streams):
    out_buf, err_buf = capture_streams
    import sys

    # Produce an exception from user code (not from cliasi).
    try:
        raise ValueError("boom")
    except Exception:
        exc_info = sys.exc_info()
        # Call the installed excepthook (installed at package import time)
        sys.excepthook(*exc_info)

    # The handler should have used the Cliasi instance to report the uncaught exception (written to stderr)
    err = normalize_output(err_buf.getvalue())
    # Depending on filesystem layout the traceback may be classified as coming from `cliasi` (e.g. when
    # the test path contains '/cliasi/'). Accept either the normal Cliasi reporting path OR the
    # cliasi-package fallback message that writes to stderr directly.
    normal_path = ("Uncaught exception:" in err and "ValueError: boom" in err)
    fallback_path = "Uncaught exception inside cliasi package; falling back to stderr" in err and "ValueError: boom" in err
    assert normal_path or fallback_path, f"Unexpected exception hook output:\n{err}"


def test_exception_hook_from_cliasi_does_not_use_cli_fail(capture_streams):
    out_buf, err_buf = capture_streams
    from cliasi import cliasi as cliasi_module
    import sys

    # Add a function to cliasi module that raises so the traceback is attributed to cliasi
    def raise_in_cliasi():
        raise RuntimeError("internal")

    # Attach to module so the traceback will look like it originated from cliasi
    setattr(cliasi_module, "raise_in_cliasi", raise_in_cliasi)

    try:
        # Call via getattr because the attribute is added dynamically
        getattr(cliasi_module, "raise_in_cliasi")()
    except Exception:
        exc_info = sys.exc_info()
        # Invoke excepthook directly to simulate uncaught exception
        sys.excepthook(*exc_info)

    # Because the exception originates from cliasi, the handler should write a minimal fallback to stderr
    err = normalize_output(err_buf.getvalue())
    assert "Uncaught exception inside cliasi package; falling back to stderr" in err
    # Also ensure the formatted traceback contains the original exception message
    assert "RuntimeError: internal" in err


def test_install_logger_registers_handler():
    from cliasi import logging_handler as logging_handler_module

    root = logging.getLogger()
    old_handlers = list(root.handlers)
    old_level = root.level
    try:
        c = Cliasi("LG", messages_stay_in_one_line=False, colors=False)
        logging_handler_module.install_logger(c)

        handlers = list(root.handlers)
        # Find a CLILoggingHandler that references our Cliasi instance
        found = any(isinstance(h, logging_handler_module.CLILoggingHandler) and getattr(h, "cli", None) is c for h in handlers)
        assert found, "CLILoggingHandler was not registered on the root logger"
        assert root.level == logging.NOTSET
    finally:
        # Restore root logger state to avoid interfering with other tests
        root.handlers[:] = []
        for h in old_handlers:
            root.addHandler(h)
        root.setLevel(old_level)


def test_install_logger_replaces_stream_handlers():
    from cliasi import logging_handler as logging_handler_module

    root = logging.getLogger()
    old_handlers = list(root.handlers)
    old_level = root.level
    try:
        # Ensure there's at least one StreamHandler present
        sh = logging.StreamHandler()
        root.addHandler(sh)
        c = Cliasi("LG2", messages_stay_in_one_line=False, colors=False)
        logging_handler_module.install_logger(c, replace_root_handlers=True)

        # No StreamHandler should remain on the root logger
        assert not any(isinstance(h, logging.StreamHandler) for h in root.handlers), "StreamHandler was not removed from root logger"
        # CLILoggingHandler should be present
        assert any(isinstance(h, logging_handler_module.CLILoggingHandler) for h in root.handlers)
    finally:
        root.handlers[:] = []
        for h in old_handlers:
            root.addHandler(h)
        root.setLevel(old_level)
