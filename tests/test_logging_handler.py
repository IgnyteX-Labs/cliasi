import io
import logging
import re
import sys

import pytest

from cliasi import Cliasi
from cliasi.logging_handler import (
    CLILoggingHandler,
    install_exception_hook,
)

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def normalize_output(s: str) -> str:
    # Remove ANSI codes and carriage/clear sequences, collapse spaces
    s = ANSI_RE.sub("", s)
    s = s.replace("\r", "").replace("\n", "\n").replace("\x1b[2K", "")
    return s.strip()


@pytest.fixture
def capture_streams(monkeypatch):
    out_buf = io.StringIO()
    err_buf = io.StringIO()

    import cliasi.cliasi as cc
    import cliasi.logging_handler as lh

    monkeypatch.setattr(lh, "STDERR_STREAM", err_buf)
    monkeypatch.setattr(cc, "STDOUT_STREAM", out_buf)
    monkeypatch.setattr(cc, "STDERR_STREAM", err_buf)

    return out_buf, err_buf


def test_cli_logging_handler_emit_info(capture_streams):
    out_buf, err_buf = capture_streams
    cli = Cliasi("TEST", colors=False)
    handler = CLILoggingHandler(cli)

    logger = logging.getLogger("test_info")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("info message")

    output = normalize_output(out_buf.getvalue())
    assert "i [TEST] | info message" in output


def test_cli_logging_handler_emit_error_with_exc_info(capture_streams):
    out_buf, err_buf = capture_streams
    cli = Cliasi("TEST", colors=False)
    handler = CLILoggingHandler(cli)

    logger = logging.getLogger("test_error")
    logger.addHandler(handler)

    try:
        raise ValueError("error message")
    except ValueError:
        logger.error("caught error", exc_info=True)

    output = normalize_output(err_buf.getvalue())
    assert "X [TEST] | caught error" in output
    assert "ValueError: error message" in output


def test_exception_hook_user_code(capture_streams, monkeypatch):
    out_buf, err_buf = capture_streams
    cli = Cliasi("TEST", colors=False)
    install_exception_hook(cli)

    def mock_excepthook(type, value, tb):
        pass

    monkeypatch.setattr(sys, "__excepthook__", mock_excepthook)

    try:
        raise RuntimeError("user error")
    except RuntimeError:
        sys.excepthook(*sys.exc_info())

    output = normalize_output(err_buf.getvalue())
    assert "X [TEST] | Uncaught exception:" in output
    assert "RuntimeError: user error" in output


def test_exception_hook_cliasi_code(capture_streams, monkeypatch):
    out_buf, err_buf = capture_streams
    cli = Cliasi("TEST", colors=False)
    install_exception_hook(cli)

    # We need to simulate an exception coming from cliasi.
    # We'll use a frame that has "cliasi" in its module name.

    def raise_cliasi_error():
        raise RuntimeError("cliasi error")

    # Inject function into cliasi module so its __name__ becomes cliasi.cliasi
    # Wait, functions defined in this file will have __module__ = tests.test_logging_handler
    # even if we attach them to another module.

    # Let's try to mock the frame's globals.

    try:
        raise_cliasi_error()
    except RuntimeError:
        type, value, tb = sys.exc_info()
        # Mock the frame's globals to include cliasi in __name__
        monkeypatch.setitem(tb.tb_frame.f_globals, "__name__", "cliasi.something")
        sys.excepthook(type, value, tb)

    output = normalize_output(err_buf.getvalue())
    assert (
        "! [cliasi] Uncaught exception inside cliasi package; falling back to stderr"
        in output
    )
    assert "RuntimeError: cliasi error" in output


def test_exception_hook_keyboard_interrupt(capture_streams, monkeypatch):
    out_buf, err_buf = capture_streams
    cli = Cliasi("TEST", colors=False)
    install_exception_hook(cli)

    called = []

    def mock_excepthook(type, value, tb):
        called.append(True)

    monkeypatch.setattr(sys, "__excepthook__", mock_excepthook)

    try:
        raise KeyboardInterrupt()
    except KeyboardInterrupt:
        sys.excepthook(*sys.exc_info())

    assert called == [True]
    assert err_buf.getvalue() == ""


def test_exception_hook_fail_raises(capture_streams, monkeypatch):
    out_buf, err_buf = capture_streams
    cli = Cliasi("TEST", colors=False)

    def broken_fail(*args, **kwargs):
        raise RuntimeError("fail itself failed")

    monkeypatch.setattr(cli, "fail", broken_fail)
    install_exception_hook(cli)

    try:
        raise ValueError("original error")
    except ValueError:
        sys.excepthook(*sys.exc_info())

    output = normalize_output(err_buf.getvalue())
    assert (
        "! [cliasi] Failed while reporting uncaught exception via Cliasi; writing to stderr"
        in output
    )
    assert "ValueError: original error" in output
    # It should NOT contain "fail itself failed" in the final output to the user,
    # but the original traceback should be there.
    assert "RuntimeError: fail itself failed" not in output
