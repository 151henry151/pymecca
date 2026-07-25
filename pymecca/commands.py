"""
Shared command language for ``pymecca repl`` and the persistent session.

Each command is a single line. Verbs match the interactive REPL; a few
plain-English aliases (e.g. ``raise right arm``) are accepted too.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol

from . import protocol


class CommandOutcome(Enum):
    OK = auto()
    ERROR = auto()
    HELP = auto()
    QUIT = auto()


@dataclass(frozen=True)
class CommandResult:
    outcome: CommandOutcome
    message: str = ""

    @property
    def ok(self) -> bool:
        return self.outcome in (CommandOutcome.OK, CommandOutcome.HELP, CommandOutcome.QUIT)


class RobotCommands(Protocol):
    """
    Minimal async robot surface used by the command dispatcher.
    """

    async def servo(self, servo: int, value: int) -> None: ...
    async def servo_light(self, servo: int, color: int | str) -> None: ...
    async def chest_light(self, light: int, on: bool) -> None: ...
    async def eye_lights(self, r: int, g: int, b: int) -> None: ...
    async def drive(self, left_speed: int = 0, right_speed: int = 0) -> None: ...
    async def stop(self) -> None: ...
    async def behaviour(self, *args: int) -> None: ...
    async def send_raw(self, frame: bytes) -> None: ...


COMMAND_HELP = """\
Commands:
  servo N VALUE        move servo N (0-7) to VALUE (0-255, 128 = centre)
  light N COLOUR       set servo N's LED (off/red/green/yellow/blue/magenta/cyan/white)
  chest N on|off       chest LED N (0-3)
  eyes R G B           eye colour, each channel 0-7
  eyes COLOUR          eye colour by name (off/red/green/blue/white/yellow/magenta/cyan)
  drive LEFT RIGHT     wheel speeds, -255..255 (0 0 stops)
  stop                 stop the wheels
  behaviour B [...]    raw opcode-0x19 bytes (experiment!)
  raw B B B ...        send 18 raw bytes (checksum added for you)
  raise|lower left|right arm
  right hand forward   right hand out in front (shoulder centre + elbow front)
  arms up|hands up     both shoulders to the sky
  help                 this text
  quit                 disconnect and exit (repl / session shutdown from repl)
"""

_EYE_COLOURS = {
    "off": (0, 0, 0),
    "black": (0, 0, 0),
    "red": (7, 0, 0),
    "green": (0, 7, 0),
    "blue": (0, 0, 7),
    "white": (7, 7, 7),
    "yellow": (7, 7, 0),
    "magenta": (7, 0, 7),
    "cyan": (0, 7, 7),
}

# Observed on this humanoid build (see docs/SERVO_MAP.md). Stock Servo
# enum names disagree with the wiring — prefer these slot numbers.
LEFT_SHOULDER_SLOT = 0
LEFT_ELBOW_SLOT = 1
RIGHT_SHOULDER_SLOT = 2
RIGHT_ELBOW_SLOT = 3

# Shoulder targets (logical values sent through pymecca).
LEFT_SHOULDER_UP = 0x00
LEFT_SHOULDER_DOWN = 0xFF
RIGHT_SHOULDER_UP = 0xFF
RIGHT_SHOULDER_CENTRE = 0x80
RIGHT_SHOULDER_DOWN = 0x00

# Elbow targets (logical).
LEFT_ELBOW_FRONT = 0xFF
LEFT_ELBOW_BACK = 0x00
RIGHT_ELBOW_FRONT = 0x00
RIGHT_ELBOW_BACK = 0xFF

ARM_NUDGE_STEP = 0x20

_SHOULDER_POSE = {
    ("raise", "right"): (RIGHT_SHOULDER_SLOT, RIGHT_SHOULDER_UP),
    ("lower", "right"): (RIGHT_SHOULDER_SLOT, RIGHT_SHOULDER_CENTRE),
    ("raise", "left"): (LEFT_SHOULDER_SLOT, LEFT_SHOULDER_UP),
    ("lower", "left"): (LEFT_SHOULDER_SLOT, LEFT_SHOULDER_DOWN),
}


def _ok(message: str = "") -> CommandResult:
    return CommandResult(CommandOutcome.OK, message)


def _err(message: str) -> CommandResult:
    return CommandResult(CommandOutcome.ERROR, message)


def normalize_line(line: str) -> str:
    """
    Collapse whitespace and strip a trailing comment.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return ""
    return " ".join(line.split())


def _parse_arm_alias(parts: list[str]) -> tuple[str, str] | None:
    """
    Match ``raise|lower [the] left|right arm``.
    Returns ``(action, side)`` or None.
    """
    if len(parts) < 3:
        return None
    action = parts[0].lower()
    if action not in ("raise", "lower"):
        return None
    rest = [p.lower() for p in parts[1:]]
    if rest and rest[0] == "the":
        rest = rest[1:]
    if len(rest) != 2 or rest[1] != "arm":
        return None
    side = rest[0]
    if (action, side) not in _SHOULDER_POSE:
        return None
    return action, side


def _pose_core(parts: list[str]) -> list[str]:
    words = [p.lower() for p in parts]
    return [w for w in words if w not in {"the", "a", "of", "you", "your", "put", "both"}]


def _is_right_hand_forward(parts: list[str]) -> bool:
    """
    Match short or long forms of the confirmed right-hand-forward pose.
    """
    core = _pose_core(parts)
    return core in (
        ["right", "hand", "forward"],
        ["right", "hand", "out", "in", "front"],
        ["right", "hand", "out", "front"],
    )


def _is_arms_up(parts: list[str]) -> bool:
    core = _pose_core(parts)
    return core in (
        ["arms", "up"],
        ["hands", "up"],
        ["hands", "in", "the", "air"],
        ["hands", "in", "air"],
    )


def clamp_servo(value: int) -> int:
    return max(0x00, min(0xFF, int(value)))


async def apply_right_hand_forward(bot: RobotCommands) -> None:
    await bot.servo(RIGHT_SHOULDER_SLOT, RIGHT_SHOULDER_CENTRE)
    await bot.servo(RIGHT_ELBOW_SLOT, RIGHT_ELBOW_FRONT)


async def apply_arms_up(bot: RobotCommands) -> None:
    await bot.servo(LEFT_SHOULDER_SLOT, LEFT_SHOULDER_UP)
    await bot.servo(RIGHT_SHOULDER_SLOT, RIGHT_SHOULDER_UP)


async def dispatch(bot: RobotCommands, line: str) -> CommandResult:
    """
    Execute one command line against ``bot``.
    """
    text = normalize_line(line)
    if not text:
        return _ok()

    parts = text.split()
    cmd = parts[0].lower()
    rest = parts[1:]

    try:
        arm = _parse_arm_alias(parts)
        if arm is not None:
            action, side = arm
            slot, value = _SHOULDER_POSE[(action, side)]
            await bot.servo(slot, value)
            return _ok(f"{action} {side} arm")

        if _is_right_hand_forward(parts):
            await apply_right_hand_forward(bot)
            return _ok("right hand forward")

        if _is_arms_up(parts):
            await apply_arms_up(bot)
            return _ok("arms up")

        if cmd in ("quit", "exit", "q"):
            return CommandResult(CommandOutcome.QUIT)

        if cmd == "help":
            return CommandResult(CommandOutcome.HELP, COMMAND_HELP)

        if cmd == "ping":
            return _ok("connected")

        if cmd == "servo":
            await bot.servo(int(rest[0], 0), int(rest[1], 0))
            return _ok()

        if cmd == "light":
            await bot.servo_light(int(rest[0], 0), rest[1])
            return _ok()

        if cmd == "chest":
            await bot.chest_light(int(rest[0], 0), rest[1].lower() in ("on", "1", "true"))
            return _ok()

        if cmd == "eyes":
            if len(rest) == 1:
                colour = rest[0].lower()
                if colour not in _EYE_COLOURS:
                    return _err(
                        f"unknown eye colour {rest[0]!r}; "
                        f"try {', '.join(sorted(_EYE_COLOURS))}"
                    )
                await bot.eye_lights(*_EYE_COLOURS[colour])
                return _ok()
            await bot.eye_lights(int(rest[0], 0), int(rest[1], 0), int(rest[2], 0))
            return _ok()

        if cmd == "drive":
            await bot.drive(int(rest[0], 0), int(rest[1], 0))
            return _ok()

        if cmd == "stop":
            await bot.stop()
            return _ok()

        if cmd in ("behaviour", "behavior"):
            await bot.behaviour(*(int(x, 0) for x in rest))
            return _ok()

        if cmd == "raw":
            await bot.send_raw(protocol.frame([int(x, 0) for x in rest]))
            return _ok()

        return _err(f"unknown command: {cmd} (try 'help')")

    except (ValueError, IndexError, TypeError, KeyError) as e:
        return _err(f"bad arguments: {e}")
    except Exception as e:  # noqa: BLE001 -- surface robot/BLE errors to the client
        return _err(str(e))


def format_reply(result: CommandResult) -> str:
    """
    One-line socket/CLI reply for a :class:`CommandResult`.
    """
    if result.outcome == CommandOutcome.ERROR:
        return f"error: {result.message}" if result.message else "error"
    if result.outcome == CommandOutcome.HELP:
        return result.message.rstrip("\n")
    if result.outcome == CommandOutcome.QUIT:
        return "ok quit"
    if result.message:
        return f"ok {result.message}"
    return "ok"
