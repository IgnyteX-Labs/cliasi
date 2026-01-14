import io
import re
import sys

import pytest

from cliasi import Cliasi

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def normalize_output(s: str) -> str:
    # Remove ANSI codes and carriage/clear sequences
    s = ANSI_RE.sub("", s)
    s = s.replace("\r", "").replace("\x1b[2K", "")
    return s


@pytest.fixture()
def fixed_width(monkeypatch):
    from cliasi import cliasi as cliasi_module

    monkeypatch.setattr(cliasi_module, "_terminal_size", lambda: 80)
    yield


@pytest.fixture()
def capture_streams(monkeypatch):
    from cliasi import cliasi as cliasi_module
    from cliasi import logging_handler as logging_handler_module

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(cliasi_module, "STDOUT_STREAM", out_buf)
    monkeypatch.setattr(cliasi_module, "STDERR_STREAM", err_buf)
    monkeypatch.setattr(logging_handler_module, "STDERR_STREAM", err_buf)
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    yield out_buf, err_buf


def test_one_line_full_alignment(fixed_width, capture_streams):
    out_buf, _ = capture_streams
    c = Cliasi("TEST", colors=False)
    # content_space should be 80 - (len("i") + 1 + len("[TEST]") + 1 + len("|") + 1) = 80 - (1 + 1 + 6 + 1 + 1 + 1) = 69
    # Wait, prefix [TEST] is length 6.
    c.info("Left", message_center="Center", message_right="Right")
    out = normalize_output(out_buf.getvalue())
    line = out.splitlines()[0]
    assert "Left" in line
    assert "Center" in line
    assert "Right" in line
    # Check that Right is at the end of the line (ignoring trailing whitespace from print if any)
    assert line.rstrip().endswith("Right")
    # Check that Center is roughly in the middle
    assert line.find("Center") > line.find("Left")
    assert line.find("Right") > line.find("Center")


def test_one_line_overlap_fallback(fixed_width, capture_streams):
    out_buf, _ = capture_streams
    c = Cliasi("TEST", colors=False)
    # content_space is 68.
    # L=30, C=20, R=15. Total min length = 30+1+20+1+15 = 67. Fits in 68.
    # Center will overlap and be pushed. Right will just fit aligned at the end.
    c.info("L" * 30, message_center="C" * 20, message_right="R" * 15)
    out = normalize_output(out_buf.getvalue())
    assert "LLLL" in out
    assert "CCCC" in out
    assert "RRRR" in out
    # Check they are in order
    assert out.find("L" * 30) < out.find("C" * 20)
    assert out.find("C" * 20) < out.find("R" * 15)


def test_right_multiline_too_long(fixed_width, capture_streams):
    out_buf, _ = capture_streams
    c = Cliasi("TEST", colors=False)
    # content_space is 69.
    # message_right longer than content_space
    right = "R" * 75
    c.info("Left", message_right=right)
    out = normalize_output(out_buf.getvalue())
    # It should wrap. "Left" + "RRR..."
    # The current logic for too long right message just appends it to content_to_split.
    assert "LeftRRR" in out.replace("\n", "").replace(" ", "")


def test_right_fit_last_line(fixed_width, capture_streams):
    out_buf, _ = capture_streams
    c = Cliasi("TEST", colors=False)
    # message_left takes 1.5 lines. Last line has space for message_right.
    # 69 * 1.5 = 103.
    left = "L" * 80
    # Line 1: 69 chars. Line 2: 11 chars.
    # 69 - 11 = 58 available on last line.
    right = "RIGHT"
    c.info(left, message_right=right)
    out = normalize_output(out_buf.getvalue())
    lines = out.splitlines()
    assert len(lines) >= 2
    assert right in lines[-1]
    assert lines[-1].rstrip().endswith(right)


def test_right_no_fit_last_line(fixed_width, capture_streams):
    out_buf, _ = capture_streams
    c = Cliasi("TEST", colors=False)
    # message_left takes almost full line on last line.
    # 69 * 1.9 = 131.
    left = "L" * 135
    # Line 1: 69. Line 2: 66.
    # 69 - 66 = 3. Not enough for "RIGHT" (5) + 1 space.
    right = "RIGHT"
    c.info(left, message_right=right)
    out = normalize_output(out_buf.getvalue())
    lines = out.splitlines()
    assert len(lines) >= 3
    assert right in lines[-1]
