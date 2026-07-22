"""
Unit tests for the pure-Python protocol layer.
"""

import pytest

from pymecca import protocol
from pymecca.protocol import (
    Color,
    MeccanoidState,
    Servo,
    behaviour_frame,
    checksum,
    clamp_byte,
    drive_frame,
    eye_lights_frame,
    frame,
    parse_color,
    wake_frame,
)

# ----------------------------------------------------------------------
# Framing / checksum

def test_checksum_simple():
    assert checksum(bytes([1, 2, 3])) == bytes([0x00, 0x06])


def test_checksum_carries_into_high_byte():
    data = bytes([0xFF] * 18)
    total = 0xFF * 18
    assert checksum(data) == bytes([(total >> 8) & 0xFF, total & 0xFF])


def test_frame_is_20_bytes():
    f = frame(bytes(18))
    assert len(f) == protocol.FRAME_LENGTH == 20
    assert f == bytes(20)


def test_frame_rejects_wrong_length():
    with pytest.raises(ValueError):
        frame(bytes(17))
    with pytest.raises(ValueError):
        frame(bytes(19))


def test_frame_matches_original_pymecca_checksum():
    # The original code appended (sum >> 8) & 0xff then sum & 0xff.
    cmd = tuple(range(18))
    total = sum(cmd)
    assert frame(cmd)[-2:] == bytes([(total >> 8) & 0xFF, total & 0xFF])


def test_clamp_byte():
    assert clamp_byte(-5) == 0
    assert clamp_byte(0) == 0
    assert clamp_byte(128) == 128
    assert clamp_byte(300) == 255


# ----------------------------------------------------------------------
# Colours

def test_parse_color_names_and_ints():
    assert parse_color("red") == Color.RED
    assert parse_color("OFF") == Color.OFF
    assert parse_color("black") == Color.OFF
    assert parse_color("on") == Color.WHITE
    assert parse_color(6) == Color.CYAN
    assert parse_color(Color.BLUE) == Color.BLUE


def test_parse_color_rejects_junk():
    with pytest.raises(ValueError):
        parse_color("purple")
    with pytest.raises(ValueError):
        parse_color(8)


def test_color_is_rgb_bitmask():
    assert Color.YELLOW == Color.RED | Color.GREEN
    assert Color.CYAN == Color.GREEN | Color.BLUE
    assert Color.MAGENTA == Color.RED | Color.BLUE
    assert Color.WHITE == Color.RED | Color.GREEN | Color.BLUE


# ----------------------------------------------------------------------
# Servos

def test_set_servo_updates_position():
    state = MeccanoidState()
    f = state.set_servo(Servo.RIGHT_SHOULDER, 0x40)
    assert f[0] == 0x08
    assert f[1 + Servo.RIGHT_SHOULDER] == 0x40


def test_set_servo_reverses_mirrored_servos():
    state = MeccanoidState()
    f = state.set_servo(Servo.LEFT_SHOULDER, 0x40)
    assert f[1 + Servo.LEFT_SHOULDER] == 0xFF - 0x40
    f = state.set_servo(Servo.RIGHT_ELBOW, 0x00)
    assert f[1 + Servo.RIGHT_ELBOW] == 0xFF
    # Centre stays centred (0xff - 0x80 would be 0x7f, off by one).
    f = state.set_servo(Servo.LEFT_SHOULDER, 0x80)
    assert f[1 + Servo.LEFT_SHOULDER] == 0x80


def test_set_servo_clamps_value():
    state = MeccanoidState()
    f = state.set_servo(Servo.RIGHT_SHOULDER, 999)
    assert f[1 + Servo.RIGHT_SHOULDER] == 0xFF


def test_set_servo_rejects_bad_index():
    state = MeccanoidState()
    with pytest.raises(ValueError):
        state.set_servo(8, 0x80)
    with pytest.raises(ValueError):
        state.set_servo(-1, 0x80)


def test_set_servo_is_stateful():
    state = MeccanoidState()
    state.set_servo(Servo.RIGHT_SHOULDER, 0x10)
    f = state.set_servo(Servo.LEFT_ELBOW, 0x20)
    assert f[1 + Servo.RIGHT_SHOULDER] == 0x10
    assert f[1 + Servo.LEFT_ELBOW] == 0x20


# ----------------------------------------------------------------------
# Lights

def test_set_servo_light():
    state = MeccanoidState()
    f = state.set_servo_light(3, "magenta")
    assert f[0] == 0x0C
    assert f[1 + 3] == Color.MAGENTA


def test_set_chest_light():
    state = MeccanoidState()
    f = state.set_chest_light(2, True)
    assert f[0] == 0x1C
    assert f[1 + 2] == 0x01
    f = state.set_chest_light(2, False)
    assert f[1 + 2] == 0x00
    with pytest.raises(ValueError):
        state.set_chest_light(4, True)


def test_eye_lights_packing():
    f = eye_lights_frame(7, 0, 0)
    assert f[0] == 0x11
    assert f[3] == 0x07  # red in the low bits
    assert f[4] == 0x00
    f = eye_lights_frame(0, 7, 0)
    assert f[3] == 7 << 3  # green shifted up
    f = eye_lights_frame(0, 0, 7)
    assert f[3] == 0x00
    assert f[4] == 0x07  # blue in its own byte
    # Out-of-range channels are clamped, not errors.
    assert eye_lights_frame(99, -1, 3)[3] == 0x07
    assert eye_lights_frame(99, -1, 3)[4] == 0x03


# ----------------------------------------------------------------------
# Wheels

def test_drive_forward():
    f = drive_frame(100, 200)
    assert f[0] == 0x0D
    assert f[1] == 0x01  # left forward
    assert f[2] == 0x01  # right forward
    assert f[3] == 100
    assert f[4] == 200


def test_drive_backward():
    f = drive_frame(-100, -200)
    assert f[1] == 0x02
    assert f[2] == 0x02
    assert f[3] == 100
    assert f[4] == 200


def test_drive_stop_uses_neutral_direction():
    # The original code sent direction 0x02 (backwards) for zero speed;
    # a stop should be direction 0x00.
    f = drive_frame(0, 0)
    assert f[1] == 0x00
    assert f[2] == 0x00
    assert f[3] == 0x00
    assert f[4] == 0x00


def test_drive_clamps_speed():
    f = drive_frame(999, -999)
    assert f[3] == 0xFF
    assert f[4] == 0xFF


# ----------------------------------------------------------------------
# Behaviours

def test_wake_frame_matches_original():
    # The exact byte string the original library sent on connect.
    original = (0x19,) + (0x1D,) * 17
    assert wake_frame()[:18] == bytes(original)


def test_behaviour_frame_pads_and_validates():
    f = behaviour_frame(0x1D)
    assert f[0] == 0x19
    assert f[1] == 0x1D
    assert f[2:18] == bytes(16)
    with pytest.raises(ValueError):
        behaviour_frame(*([0] * 18))
