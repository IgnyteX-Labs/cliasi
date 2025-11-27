import re
import time

import pytest

from cliasi import Cliasi, cli


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


def test_basic_messages_symbols_and_message(capsys):
    c = Cliasi("TEST", use_oneline=False, colors=False)

    c.info("hello")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("i [TEST]")
    assert "| hello" in out

    c.warn("be careful")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("! [TEST]")
    assert "| be careful" in out

    c.success("ok")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("✔ [TEST]")
    assert "| ok" in out

    c.fail("nope")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("X [TEST]")
    assert "| nope" in out

    c.log("logged")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("LOG [TEST]")
    assert "| logged" in out

    c.neutral("meh")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("# [TEST]")
    assert "| meh" in out


def test_update_prefix_and_separator(capsys):
    c = Cliasi("OLD", use_oneline=False, colors=False, seperator="|")
    c.update_prefix("NEW")
    c.info("msg")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("i [NEW]")
    assert "| msg" in out

    c.prefix_seperator = "::"
    c.info("again")
    out = normalize_output(capsys.readouterr().out)
    assert ":: again" in out


def test_verbosity_filters(capsys):
    c = Cliasi("V", use_oneline=False, colors=False, min_verbose_level=1)
    # According to current implementation, level > min is suppressed
    # lower or equal -> shown
    c.info("visible", verbosity=0)
    out = normalize_output(capsys.readouterr().out)
    assert "visible" in out
    # higher than min -> suppressed
    c.info("hidden", verbosity=2)
    out = capsys.readouterr().out
    assert out == ""


def test_oneline_override_prints_no_newline(capsys):
    c = Cliasi("OL", use_oneline=False, colors=False)
    c.info("same line", oneline_override=True)
    captured = capsys.readouterr()
    # Should not end with a newline because oneline keeps it on the same line
    assert not captured.out.endswith("\n")


def test_progressbar_static(fixed_width, capsys):
    c = Cliasi("PB", use_oneline=False, colors=False)
    c.progressbar("Working", progress=50, oneline_override=False, show_percent=True)
    out = normalize_output(capsys.readouterr().out)
    assert "[" in out and "]" in out
    assert "50%" in out

    c.progressbar_download("Downloading", progress=10, show_percent=False)
    out = normalize_output(capsys.readouterr().out)
    assert "[" in out and "]" in out


def test_non_blocking_animation_starts_and_stops(capsys):
    c = Cliasi("AN", use_oneline=True, colors=False)
    task = c.animate_message_non_blocking("Wait", interval=0.01)
    time.sleep(0.03)
    task.stop()
    out = normalize_output(capsys.readouterr().out)
    # At least one animation frame or the trailing newline from stop()
    assert "[" in out or "Wait" in out or out != ""


def test_non_blocking_progressbar_update_and_stop(fixed_width, capsys):
    c = Cliasi("APB", use_oneline=True, colors=False)
    task = c.progressbar_animated_normal("Doing", progress=0, interval=0.01, show_percent=True)
    time.sleep(0.02)
    task.update(25)
    time.sleep(0.02)
    task.stop()
    out = normalize_output(capsys.readouterr().out)
    assert "Doing" in out or "25%" in out or "[" in out


def test_default_cli_instance_is_usable(capsys):
    # Using the shared instance exported as `cli`
    cli.info("shared works")
    out = normalize_output(capsys.readouterr().out)
    assert "shared works" in out
