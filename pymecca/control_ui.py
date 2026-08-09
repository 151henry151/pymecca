"""
Terminal control panel for live Meccanoid teleop.

Hold arrow keys / WASD to drive (release = stop). Arms, eyes, and speed
use one-shot keys. The on-screen panel always shows connection status and
the key map.
"""

from __future__ import annotations

import asyncio
import logging
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path

from .commands import (
    ARM_NUDGE_STEP,
    LEFT_ELBOW_FRONT,
    LEFT_ELBOW_SLOT,
    LEFT_SHOULDER_CENTRE,
    LEFT_SHOULDER_DOWN,
    LEFT_SHOULDER_SLOT,
    LEFT_SHOULDER_UP,
    RIGHT_ELBOW_FRONT,
    RIGHT_ELBOW_SLOT,
    RIGHT_SHOULDER_CENTRE,
    RIGHT_SHOULDER_DOWN,
    RIGHT_SHOULDER_SLOT,
    RIGHT_SHOULDER_UP,
    apply_arms_down,
    apply_arms_up,
    apply_laser_ready,
    apply_left_hand_forward,
    apply_right_hand_forward,
    clamp_servo,
)
from .robot import Meccanoid, NotConnectedError, discover
from .session import session_dir

_TICK_S = 0.05
_DRIVE_KEYS = frozenset({"w", "a", "s", "d", "up", "down", "left", "right"})
_LAST_ADDRESS_NAME = "last_address"


def _last_address_path() -> Path:
    return session_dir() / _LAST_ADDRESS_NAME


def _read_last_address() -> str | None:
    path = _last_address_path()
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _write_last_address(address: str) -> None:
    path = _last_address_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(address.strip() + "\n", encoding="utf-8")
    except OSError:
        pass

_EYE_CYCLE: list[tuple[str, tuple[int, int, int]]] = [
    ("off", (0, 0, 0)),
    ("red", (7, 0, 0)),
    ("green", (0, 7, 0)),
    ("blue", (0, 0, 7)),
    ("white", (7, 7, 7)),
    ("yellow", (7, 7, 0)),
    ("magenta", (7, 0, 7)),
    ("cyan", (0, 7, 7)),
]

_EYE_HOTKEYS = {
    "z": "off",
    "x": "red",
    "c": "green",
    "v": "blue",
    "b": "white",
    "n": "yellow",
    "m": "magenta",
    ",": "cyan",
}


@dataclass
class _PanelState:
    address: str
    connected: bool = False
    connecting: bool = False
    status_note: str = "starting…"
    speed: int = 150
    motion_label: str = "stopped"
    eye_name: str = "blue"
    eye_rgb: tuple[int, int, int] = (0, 0, 7)
    arms: dict[int, int] = field(
        default_factory=lambda: {
            LEFT_SHOULDER_SLOT: 0x7F,
            LEFT_ELBOW_SLOT: 0x80,
            RIGHT_SHOULDER_SLOT: RIGHT_SHOULDER_CENTRE,
            RIGHT_ELBOW_SLOT: 0x80,
        }
    )
    last_action: str = "—"
    quit_requested: bool = False


class _QuietTerminal:
    """Disable echo/canonical mode so teleop keystrokes do not clutter the TTY."""

    def __enter__(self):
        if sys.platform == "win32":
            return self
        import termios
        import tty

        self._fd = sys.stdin.fileno()
        self._old = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)
        return self

    def __exit__(self, *exc):
        if sys.platform != "win32":
            import termios

            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)


class _HoldKeys:
    """Track held keys via press/release (pynput)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._held: set[str] = set()
        self._presses: asyncio.Queue[str] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._listener = None

    def __enter__(self) -> _HoldKeys:
        from pynput import keyboard

        self._loop = asyncio.get_running_loop()
        self._presses = asyncio.Queue()

        def on_press(key: object) -> None:
            ch = _HoldKeys._normalize(key, keyboard)
            if ch is None:
                return
            with self._lock:
                first = ch not in self._held
                self._held.add(ch)
            if first and self._loop is not None and self._presses is not None:
                self._loop.call_soon_threadsafe(self._presses.put_nowait, ch)

        def on_release(key: object) -> None:
            ch = _HoldKeys._normalize(key, keyboard)
            if ch is None:
                return
            with self._lock:
                self._held.discard(ch)

        self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._listener.start()
        return self

    def __exit__(self, *exc) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def held(self) -> set[str]:
        with self._lock:
            return set(self._held)

    def drain_presses(self) -> list[str]:
        assert self._presses is not None
        out: list[str] = []
        while True:
            try:
                out.append(self._presses.get_nowait())
            except asyncio.QueueEmpty:
                return out

    @staticmethod
    def _normalize(key: object, keyboard: object) -> str | None:
        Key = keyboard.Key  # type: ignore[attr-defined]
        special = {
            Key.space: " ",
            Key.up: "up",
            Key.down: "down",
            Key.left: "left",
            Key.right: "right",
            Key.esc: "esc",
        }
        if key in special:
            return special[key]
        char = getattr(key, "char", None)
        if not char:
            return None
        return char.lower()


def _drain_stdin() -> None:
    if sys.platform == "win32" or not sys.stdin.isatty():
        return
    import select

    while select.select([sys.stdin], [], [], 0)[0]:
        if not sys.stdin.read(1):
            break


def _motion_from_held(held: set[str], speed: int) -> tuple[tuple[int, int], str] | None:
    if "w" in held or "up" in held:
        return (speed, speed), "forward"
    if "s" in held or "down" in held:
        return (-speed, -speed), "backward"
    if "a" in held or "left" in held:
        return (-speed, speed), "turn left"
    if "d" in held or "right" in held:
        return (speed, -speed), "turn right"
    return None


def _row(text: str, width: int = 62) -> str:
    if len(text) > width:
        text = text[: width - 1] + "…"
    return f"│ {text:<{width}} │"


def _render(state: _PanelState) -> str:
    if state.connecting:
        link = "CONNECTING…"
    elif state.connected:
        link = "CONNECTED"
    else:
        link = "DISCONNECTED"

    arms = state.arms
    eye = (
        f"{state.eye_name}  "
        f"rgb=({state.eye_rgb[0]},{state.eye_rgb[1]},{state.eye_rgb[2]})"
    )
    arm_line = (
        f"L-sh 0x{arms[LEFT_SHOULDER_SLOT]:02x}  "
        f"L-el 0x{arms[LEFT_ELBOW_SLOT]:02x}  "
        f"R-sh 0x{arms[RIGHT_SHOULDER_SLOT]:02x}  "
        f"R-el 0x{arms[RIGHT_ELBOW_SLOT]:02x}"
    )
    lines = [
        "┌─ pymecca control " + "─" * 44 + "┐",
        _row(f"Link:   {link}  —  {state.status_note}"),
        _row(f"Robot:  {state.address}"),
        _row(f"Motion: {state.motion_label}    Speed: {state.speed}"),
        _row(f"Eyes:   {eye}"),
        _row(f"Arms:   {arm_line}"),
        _row(f"Last:   {state.last_action}"),
        "├" + "─" * 64 + "┤",
        _row("DRIVE  (hold; release = stop)"),
        _row("  ↑ / w   forward          ↓ / s   backward"),
        _row("  ← / a   turn left        → / d   turn right"),
        _row("  space   stop"),
        _row("SPEED"),
        _row("  1-9     set speed (value = key × 28)"),
        _row("EYES"),
        _row("  e       cycle colours"),
        _row("  z off   x red   c green   v blue   b white"),
        _row("  n yellow   m magenta   , cyan"),
        _row("ARMS"),
        _row("  r / f   right shoulder up / down"),
        _row("  t / g   left shoulder up / down"),
        _row("  y / h   right elbow front / back"),
        _row("  u / j   left elbow front / back"),
        _row("  i       left hand forward       o   right hand forward"),
        _row("  p       both arms up            l   both arms down"),
        _row("SOUND"),
        _row("  k       laser-ready tone"),
        _row("APP"),
        _row("  q / esc quit"),
        _row("  c       reconnect / rescan when disconnected (else eyes green)"),
        _row("Launch tip: `pymecca control` alone scans for a Meccanoid"),
        "└" + "─" * 64 + "┘",
    ]
    return "\033[2J\033[H" + "\n".join(lines) + "\n"


def _paint(state: _PanelState) -> None:
    sys.stdout.write(_render(state))
    sys.stdout.flush()


def _eye_by_name(name: str) -> tuple[str, tuple[int, int, int]]:
    for n, rgb in _EYE_CYCLE:
        if n == name:
            return n, rgb
    return "blue", (0, 0, 7)


async def run_control(
    address: str | None = None,
    *,
    write_char=None,
    connect_timeout: float = 20.0,
    scan_timeout: float = 10.0,
) -> int:
    """
    Run the full-screen teleop panel until the user quits.

    If ``address`` is omitted, try the last successful address, then BLE-scan
    for a device whose name contains ``mecc``.
    """
    try:
        import pynput  # noqa: F401
    except ImportError:
        print(
            "Hold-to-drive needs pynput. Install with: pip install pynput",
            file=sys.stderr,
        )
        return 1

    # Bleak/pymecca disconnect warnings would trash the panel.
    logging.getLogger("pymecca.robot").setLevel(logging.ERROR)
    logging.getLogger("bleak").setLevel(logging.ERROR)

    explicit_address = address
    state = _PanelState(address=address or "(searching…)")
    bot: Meccanoid | None = None
    active_motion: tuple[int, int] | None = None
    suppress_drive = False
    eye_i = 3  # blue in _EYE_CYCLE
    needs_paint = True

    async def safe_stop() -> None:
        nonlocal active_motion
        active_motion = None
        if bot is not None and bot.is_connected:
            try:
                await bot.stop()
            except Exception:
                pass

    async def bind_bot(addr: str) -> Meccanoid:
        nonlocal bot
        if bot is not None:
            try:
                await bot.disconnect()
            except Exception:
                pass
        bot = Meccanoid(addr, write_char=write_char)
        state.address = addr
        return bot

    async def scan_for_robot() -> str | None:
        state.connecting = True
        state.connected = False
        state.address = "(scanning…)"
        state.status_note = f"BLE scan ({scan_timeout:.0f}s) for name containing 'mecc'…"
        state.last_action = "scanning…"
        _paint(state)
        found = await discover(timeout=scan_timeout)
        state.connecting = False
        if not found:
            state.address = "(none)"
            state.status_note = "no Meccanoid found — power on / free the link, then c"
            state.last_action = "scan found nothing"
            _paint(state)
            return None
        device = found[0]
        state.address = device.address
        state.status_note = f"found {device.name or 'Meccanoid'}"
        state.last_action = f"discovered {device.address}"
        _paint(state)
        return device.address

    async def resolve_address(*, force_scan: bool = False) -> str | None:
        if explicit_address and not force_scan:
            state.address = explicit_address
            state.status_note = "using address from command line"
            _paint(state)
            return explicit_address

        if not force_scan:
            last = _read_last_address()
            if last:
                state.address = last
                state.status_note = "trying last successful address…"
                state.last_action = f"saved address {last}"
                _paint(state)
                return last

        return await scan_for_robot()

    async def try_connect(*, force_scan: bool = False) -> bool:
        nonlocal bot
        addr = await resolve_address(force_scan=force_scan)
        if addr is None:
            return False
        await bind_bot(addr)

        state.connecting = True
        state.connected = False
        state.status_note = "connecting / waking robot…"
        state.motion_label = "stopped"
        _paint(state)
        try:
            assert bot is not None
            if bot.is_connected:
                await bot.disconnect()
            await bot.connect(timeout=connect_timeout)
        except Exception as exc:
            state.connecting = False
            state.connected = False
            state.status_note = f"connect failed: {exc}"
            # Cached/last address often goes stale — rescan once automatically.
            if not explicit_address and not force_scan:
                state.last_action = "connect failed — scanning…"
                _paint(state)
                return await try_connect(force_scan=True)
            state.last_action = "connect failed — press c to retry / rescan"
            _paint(state)
            return False
        state.connecting = False
        state.connected = True
        state.status_note = "ready — hold arrows/WASD to drive"
        state.eye_name, state.eye_rgb = "blue", (0, 0, 7)
        state.last_action = "connected"
        _write_last_address(addr)
        _paint(state)
        return True

    async def set_arm(slot: int, value: int, label: str) -> None:
        assert bot is not None
        value = clamp_servo(value)
        state.arms[slot] = value
        await bot.servo(slot, value)
        state.last_action = f"{label} = 0x{value:02x}"

    async def nudge(slot: int, delta: int, label: str) -> None:
        await set_arm(slot, state.arms[slot] + delta, label)

    async def set_eyes(name: str) -> None:
        assert bot is not None
        nonlocal eye_i
        name, rgb = _eye_by_name(name)
        state.eye_name, state.eye_rgb = name, rgb
        for i, (n, _) in enumerate(_EYE_CYCLE):
            if n == name:
                eye_i = i
                break
        await bot.eye_lights(*rgb)
        state.last_action = f"eyes {name}"

    # Initial discover/connect before keyboard grab so failures are readable.
    _paint(state)
    await try_connect()

    with _QuietTerminal(), _HoldKeys() as keys:
        while not state.quit_requested:
            _drain_stdin()
            state.connected = bool(bot and bot.is_connected)

            for key in keys.drain_presses():
                needs_paint = True

                if key in ("q", "esc"):
                    await safe_stop()
                    state.quit_requested = True
                    state.last_action = "quit"
                    break

                if not state.connected and not state.connecting:
                    if key == "c":
                        # Rescan when the user asks to reconnect without a fixed address.
                        await try_connect(force_scan=explicit_address is None)
                    else:
                        state.last_action = "disconnected — press c to reconnect, q to quit"
                    continue

                if key in _DRIVE_KEYS:
                    continue

                assert bot is not None
                try:
                    if key == " ":
                        suppress_drive = True
                        await safe_stop()
                        state.motion_label = "stopped"
                        state.last_action = "stop"
                    elif key == "e":
                        eye_i = (eye_i + 1) % len(_EYE_CYCLE)
                        await set_eyes(_EYE_CYCLE[eye_i][0])
                    elif key in _EYE_HOTKEYS:
                        await set_eyes(_EYE_HOTKEYS[key])
                    elif key == "r":
                        await nudge(RIGHT_SHOULDER_SLOT, ARM_NUDGE_STEP, "right shoulder")
                    elif key == "f":
                        await nudge(RIGHT_SHOULDER_SLOT, -ARM_NUDGE_STEP, "right shoulder")
                    elif key == "t":
                        await nudge(LEFT_SHOULDER_SLOT, -ARM_NUDGE_STEP, "left shoulder")
                    elif key == "g":
                        await nudge(LEFT_SHOULDER_SLOT, ARM_NUDGE_STEP, "left shoulder")
                    elif key == "y":
                        await nudge(RIGHT_ELBOW_SLOT, -ARM_NUDGE_STEP, "right elbow")
                    elif key == "h":
                        await nudge(RIGHT_ELBOW_SLOT, ARM_NUDGE_STEP, "right elbow")
                    elif key == "u":
                        await nudge(LEFT_ELBOW_SLOT, ARM_NUDGE_STEP, "left elbow")
                    elif key == "j":
                        await nudge(LEFT_ELBOW_SLOT, -ARM_NUDGE_STEP, "left elbow")
                    elif key == "i":
                        await apply_left_hand_forward(bot)
                        state.arms[LEFT_SHOULDER_SLOT] = LEFT_SHOULDER_CENTRE
                        state.arms[LEFT_ELBOW_SLOT] = LEFT_ELBOW_FRONT
                        state.last_action = "left hand forward"
                    elif key == "o":
                        await apply_right_hand_forward(bot)
                        state.arms[RIGHT_SHOULDER_SLOT] = RIGHT_SHOULDER_CENTRE
                        state.arms[RIGHT_ELBOW_SLOT] = RIGHT_ELBOW_FRONT
                        state.last_action = "right hand forward"
                    elif key == "p":
                        await apply_arms_up(bot)
                        state.arms[LEFT_SHOULDER_SLOT] = LEFT_SHOULDER_UP
                        state.arms[RIGHT_SHOULDER_SLOT] = RIGHT_SHOULDER_UP
                        state.last_action = "arms up"
                    elif key == "l":
                        await apply_arms_down(bot)
                        state.arms[LEFT_SHOULDER_SLOT] = LEFT_SHOULDER_DOWN
                        state.arms[RIGHT_SHOULDER_SLOT] = RIGHT_SHOULDER_DOWN
                        state.last_action = "arms down"
                    elif key == "k":
                        await apply_laser_ready(bot)
                        state.last_action = "laser ready"
                    elif key.isdigit() and key != "0":
                        state.speed = int(key) * 28
                        state.last_action = f"speed = {state.speed}"
                except NotConnectedError:
                    state.connected = False
                    state.status_note = "link dropped"
                    state.last_action = "disconnected — press c to reconnect"
                    await safe_stop()
                except Exception as exc:
                    state.last_action = f"error: {exc}"
                    state.status_note = "command failed"
                    if bot is None or not bot.is_connected:
                        state.connected = False

            if state.quit_requested:
                break

            held = keys.held()
            if "q" in held or "esc" in held:
                await safe_stop()
                break

            if bot is None or not bot.is_connected:
                if state.connected:
                    state.connected = False
                    state.status_note = "link dropped"
                    state.motion_label = "stopped"
                    state.last_action = "disconnected — press c to reconnect"
                    needs_paint = True
                    active_motion = None
                if needs_paint:
                    _paint(state)
                    needs_paint = False
                await asyncio.sleep(_TICK_S)
                continue

            if not held & _DRIVE_KEYS:
                suppress_drive = False

            result = None if suppress_drive else _motion_from_held(held, state.speed)
            motion = None if result is None else result[0]
            label = "stopped" if result is None else result[1]

            if motion != active_motion:
                try:
                    if motion is None:
                        await bot.stop()
                    else:
                        await bot.drive(*motion)
                    active_motion = motion
                    state.motion_label = label
                    state.last_action = label if motion is not None else "stopped"
                    needs_paint = True
                except Exception as exc:
                    state.connected = bot.is_connected
                    state.status_note = "link error while driving"
                    state.last_action = f"drive error: {exc}"
                    active_motion = None
                    state.motion_label = "stopped"
                    needs_paint = True

            if needs_paint:
                state.connected = bot.is_connected
                _paint(state)
                needs_paint = False

            await asyncio.sleep(_TICK_S)

    await safe_stop()
    if bot is not None:
        try:
            await bot.disconnect()
        except Exception:
            pass

    # Leave a clean line after the panel.
    sys.stdout.write("\nBye.\n")
    sys.stdout.flush()
    return 0
