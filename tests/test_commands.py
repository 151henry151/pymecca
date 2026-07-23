"""
Unit tests for the shared command dispatcher (no robot required).
"""

from __future__ import annotations

import asyncio

from pymecca.commands import (
    COMMAND_HELP,
    CommandOutcome,
    CommandResult,
    dispatch,
    format_reply,
    normalize_line,
)
from pymecca.protocol import Servo


class FakeBot:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    async def servo(self, servo: int, value: int) -> None:
        self.calls.append(("servo", servo, value))

    async def servo_light(self, servo: int, color) -> None:
        self.calls.append(("servo_light", servo, color))

    async def chest_light(self, light: int, on: bool) -> None:
        self.calls.append(("chest_light", light, on))

    async def eye_lights(self, r: int, g: int, b: int) -> None:
        self.calls.append(("eye_lights", r, g, b))

    async def drive(self, left_speed: int = 0, right_speed: int = 0) -> None:
        self.calls.append(("drive", left_speed, right_speed))

    async def stop(self) -> None:
        self.calls.append(("stop",))

    async def behaviour(self, *args: int) -> None:
        self.calls.append(("behaviour", args))

    async def send_raw(self, frame: bytes) -> None:
        self.calls.append(("send_raw", frame))


def _run(coro):
    return asyncio.run(coro)


def test_raise_right_arm_alias():
    bot = FakeBot()
    result = _run(dispatch(bot, "raise right arm"))
    assert result.outcome == CommandOutcome.OK
    assert bot.calls == [("servo", Servo.RIGHT_SHOULDER, 0xFF)]


def test_lower_the_left_arm_alias():
    bot = FakeBot()
    result = _run(dispatch(bot, "lower the left arm"))
    assert result.ok
    assert bot.calls == [("servo", Servo.LEFT_SHOULDER, 0x80)]


def test_eyes_named_colour():
    bot = FakeBot()
    result = _run(dispatch(bot, "eyes red"))
    assert result.outcome == CommandOutcome.OK
    assert bot.calls == [("eye_lights", 7, 0, 0)]


def test_eyes_rgb():
    bot = FakeBot()
    _run(dispatch(bot, "eyes 1 2 3"))
    assert bot.calls == [("eye_lights", 1, 2, 3)]


def test_servo_and_stop():
    bot = FakeBot()

    async def both():
        await dispatch(bot, "servo 2 0xff")
        await dispatch(bot, "stop")

    _run(both())
    assert bot.calls == [("servo", 2, 255), ("stop",)]


def test_drive():
    bot = FakeBot()
    _run(dispatch(bot, "drive -100 100"))
    assert bot.calls == [("drive", -100, 100)]


def test_chest_and_light():
    bot = FakeBot()

    async def both():
        await dispatch(bot, "chest 1 on")
        await dispatch(bot, "light 2 cyan")

    _run(both())
    assert bot.calls == [
        ("chest_light", 1, True),
        ("servo_light", 2, "cyan"),
    ]


def test_unknown_command():
    bot = FakeBot()
    result = _run(dispatch(bot, "dance"))
    assert result.outcome == CommandOutcome.ERROR
    assert "unknown" in result.message
    assert bot.calls == []


def test_bad_arguments():
    bot = FakeBot()
    result = _run(dispatch(bot, "servo"))
    assert result.outcome == CommandOutcome.ERROR
    assert result.message.startswith("bad arguments")


def test_help_and_quit():
    bot = FakeBot()
    help_result = _run(dispatch(bot, "help"))
    assert help_result.outcome == CommandOutcome.HELP
    assert "servo" in help_result.message
    assert help_result.message == COMMAND_HELP

    quit_result = _run(dispatch(bot, "quit"))
    assert quit_result.outcome == CommandOutcome.QUIT


def test_ping():
    bot = FakeBot()
    result = _run(dispatch(bot, "ping"))
    assert result.outcome == CommandOutcome.OK
    assert result.message == "connected"
    assert bot.calls == []


def test_normalize_line():
    assert normalize_line("  eyes   red  ") == "eyes red"
    assert normalize_line("# comment") == ""
    assert normalize_line("") == ""


def test_format_reply():
    assert format_reply(CommandResult(CommandOutcome.OK)) == "ok"
    assert format_reply(CommandResult(CommandOutcome.OK, "connected")) == "ok connected"
    assert format_reply(CommandResult(CommandOutcome.ERROR, "nope")) == "error: nope"
