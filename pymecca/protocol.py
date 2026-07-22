"""
The Meccanoid wire protocol.

Everything in this module is pure Python with no Bluetooth dependencies,
so it can be unit-tested without a robot present.

The Meccabrain accepts fixed-size 20-byte writes: an 18-byte command
followed by a 16-bit big-endian checksum (the plain sum of the 18
command bytes). The first command byte is an opcode; the meaning of the
rest depends on the opcode. None of this is officially documented -- it
was reverse-engineered by the community and inherited from the original
pymecca project.

Known opcodes:

===========  ==================================================
Opcode       Meaning
===========  ==================================================
``0x08``     Set all eight servo positions (one byte per servo)
``0x0C``     Set all eight servo LED colours (3-bit RGB each)
``0x0D``     Drive the wheels (direction + speed per side)
``0x11``     Set the eye LEDs (3-bit RGB, packed)
``0x19``     Trigger a built-in behaviour/sound
``0x1C``     Set the chest LEDs (on/off each)
===========  ==================================================
"""

from __future__ import annotations

from enum import IntEnum

# An 18-byte command plus a 2-byte checksum.
COMMAND_LENGTH = 18
FRAME_LENGTH = COMMAND_LENGTH + 2


class Servo(IntEnum):
    """
    The servo slots of a stock Meccanoid G15/G15KS build.

    Only four of the eight slots are used by the standard humanoid
    build; the others are available if you have wired extra smart
    servos into the Meccabrain.
    """

    UNKNOWN_0 = 0
    RIGHT_ELBOW = 1
    RIGHT_SHOULDER = 2
    LEFT_SHOULDER = 3
    LEFT_ELBOW = 4
    UNKNOWN_5 = 5
    UNKNOWN_6 = 6
    UNKNOWN_7 = 7


# On the stock build these two servos are mounted mirrored, so their
# sense is flipped in software to keep the user-facing convention
# consistent (0x00 .. 0xff sweeps every joint the same way).
REVERSED_SERVOS = frozenset({Servo.LEFT_SHOULDER, Servo.RIGHT_ELBOW})


class Color(IntEnum):
    """
    3-bit RGB colours used by the servo LEDs (bit 0 = red, bit 1 =
    green, bit 2 = blue).
    """

    OFF = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


_COLOR_NAMES = {
    "off": Color.OFF,
    "black": Color.OFF,
    "red": Color.RED,
    "green": Color.GREEN,
    "yellow": Color.YELLOW,
    "blue": Color.BLUE,
    "magenta": Color.MAGENTA,
    "cyan": Color.CYAN,
    "white": Color.WHITE,
    "on": Color.WHITE,
}

# Opcode 0x19 with these arguments makes the robot yawn and say
# "I'm awake", waggling its arms about. It is sent on connect, the same
# way the original pymecca did.
WAKE_COMMAND = bytes((0x19,) + (0x1D,) * 17)


def parse_color(value: int | str | Color) -> Color:
    """
    Turn a colour name ("red", "cyan", ...) or a 0-7 integer into a
    :class:`Color`.
    """
    if isinstance(value, str):
        try:
            return _COLOR_NAMES[value.lower()]
        except KeyError:
            raise ValueError(f"Unknown colour: {value!r}") from None
    value = int(value)
    if not 0 <= value <= 7:
        raise ValueError(f"Colour must be 0-7, got {value}")
    return Color(value)


def checksum(command: bytes | bytearray) -> bytes:
    """
    The 16-bit big-endian sum of the command bytes.
    """
    total = sum(command)
    return bytes(((total >> 8) & 0xFF, total & 0xFF))


def frame(command: bytes | bytearray | tuple) -> bytes:
    """
    Wrap an 18-byte command into the 20-byte frame the Meccabrain
    expects (command + checksum).
    """
    command = bytes(command)
    if len(command) != COMMAND_LENGTH:
        raise ValueError(
            f"Command must be {COMMAND_LENGTH} bytes, got {len(command)}"
        )
    return command + checksum(command)


def clamp_byte(value: int) -> int:
    """
    Clamp a value into the 0x00 .. 0xff range.
    """
    return max(0x00, min(0xFF, int(value)))


class MeccanoidState:
    """
    Tracks the stateful command buffers (servos, servo LEDs, chest
    LEDs) and builds ready-to-send frames.

    The Meccabrain has no "set one servo" command -- each 0x08 command
    carries all eight positions -- so the last-sent positions have to be
    remembered and mutated.
    """

    def __init__(self) -> None:
        # Default pose: arms in the same start state the original
        # library used (roughly arms-down, elbows relaxed).
        self._servos = bytearray(
            (0x08,
             0x7F, 0x80, 0x00, 0xFF, 0x80, 0x7F, 0x7F, 0x7F,
             0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01)
        )
        self._servo_lights = bytearray(
            (0x0C,
             0x00, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
             0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x00)
        )
        self._chest_lights = bytearray(
            (0x1C,
             0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00)
        )

    def servo_frame(self) -> bytes:
        """
        The frame that (re)applies the current servo pose.
        """
        return frame(self._servos)

    def set_servo(self, servo: int, value: int) -> bytes:
        """
        Set one servo position (0x00 .. 0xff) and return the frame to
        send.
        """
        servo = Servo(servo)
        value = clamp_byte(value)
        # Mirror-mounted servos run the other way; flip so the caller
        # sees a consistent direction. 0x80 is centre either way.
        if servo in REVERSED_SERVOS and value != 0x80:
            value = 0xFF - value
        self._servos[1 + servo] = value
        return frame(self._servos)

    def set_servo_light(self, servo: int, color: int | str | Color) -> bytes:
        """
        Set one servo's LED colour and return the frame to send.
        """
        servo = Servo(servo)
        self._servo_lights[1 + servo] = parse_color(color)
        return frame(self._servo_lights)

    def set_chest_light(self, light: int, on: bool) -> bytes:
        """
        Turn one of the four chest LEDs on or off and return the frame
        to send.
        """
        light = int(light)
        if not 0 <= light <= 3:
            raise ValueError(f"Chest light must be 0-3, got {light}")
        self._chest_lights[1 + light] = 0x01 if on else 0x00
        return frame(self._chest_lights)


def drive_frame(left_speed: int = 0, right_speed: int = 0) -> bytes:
    """
    Build a wheel-drive frame. Speeds are -255 .. 255; negative is
    backwards, zero stops that wheel.
    """

    def side(speed: int) -> tuple[int, int]:
        speed = int(speed)
        if speed > 0:
            return 0x01, clamp_byte(speed)
        if speed < 0:
            return 0x02, clamp_byte(-speed)
        return 0x00, 0x00

    left_dir, left = side(left_speed)
    right_dir, right = side(right_speed)
    return frame(
        (0x0D, left_dir, right_dir, left, right,
         0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
         0x00, 0x00, 0x00)
    )


def eye_lights_frame(r: int, g: int, b: int) -> bytes:
    """
    Build an eye-LED frame. Each channel is 0 .. 7.
    """
    r = min(0x7, max(0x0, int(r)))
    g = min(0x7, max(0x0, int(g)))
    b = min(0x7, max(0x0, int(b)))
    return frame(
        (0x11, 0x00, 0x00,
         (g << 3) | r,
         b,
         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
         0x00, 0x00, 0x00)
    )


def behaviour_frame(*args: int) -> bytes:
    """
    Build an opcode-0x19 behaviour/sound frame with up to 17 argument
    bytes (zero-padded). What each argument value does is largely
    unexplored -- experiment!
    """
    if len(args) > COMMAND_LENGTH - 1:
        raise ValueError("Too many arguments for a behaviour frame")
    body = tuple(clamp_byte(a) for a in args)
    body += (0x00,) * (COMMAND_LENGTH - 1 - len(body))
    return frame((0x19,) + body)


def wake_frame() -> bytes:
    """
    The "I'm awake" behaviour frame sent on connect.
    """
    return frame(WAKE_COMMAND)
