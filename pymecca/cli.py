"""
The ``pymecca`` command-line tool.

Commands:

* ``pymecca scan``              -- find your Meccanoid's address
* ``pymecca explore ADDRESS``   -- dump the robot's GATT table (debugging)
* ``pymecca demo ADDRESS``      -- connect and run a short show
* ``pymecca drive ADDRESS``     -- drive it around with the keyboard
* ``pymecca repl ADDRESS``      -- interactive command prompt
* ``pymecca session start``     -- keep a BLE link open in the background
* ``pymecca do "..."``          -- send one command to the live session

``ADDRESS`` may be omitted for the connect commands, in which case a
scan is run first and the first device with "mecc" in its name is used.
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import logging
import sys
from pathlib import Path

from bleak import BleakClient, BleakScanner

from . import protocol
from .commands import (
    ARM_NUDGE_STEP,
    COMMAND_HELP,
    LEFT_ELBOW_SLOT,
    LEFT_SHOULDER_SLOT,
    LEFT_SHOULDER_UP,
    RIGHT_ELBOW_FRONT,
    RIGHT_ELBOW_SLOT,
    RIGHT_SHOULDER_CENTRE,
    RIGHT_SHOULDER_SLOT,
    RIGHT_SHOULDER_UP,
    CommandOutcome,
    apply_arms_up,
    apply_right_hand_forward,
    clamp_servo,
    dispatch,
    format_reply,
)
from .robot import Meccanoid, discover
from .session import (
    SessionServer,
    cleanup_stale,
    read_info,
    send_command,
    session_is_live,
    spawn_background,
    stop_session,
)


def _fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


async def _resolve_address(address: str | None):
    """
    Return the given address, or scan for a Meccanoid if none given.
    """
    if address:
        return address
    print("No address given; scanning for a Meccanoid (10s)...")
    found = await discover()
    if not found:
        print(
            "No Meccanoid found. Is it powered on, in range, and not "
            "connected to the phone app? Try `pymecca scan` to see "
            "everything in range.",
            file=sys.stderr,
        )
        return None
    device = found[0]
    print(f"Found {device.name} at {device.address}")
    return device


# ----------------------------------------------------------------------
# scan

async def cmd_scan(args) -> int:
    print(f"Scanning for {args.timeout:.0f}s...")
    devices = await BleakScanner.discover(timeout=args.timeout)
    if not devices:
        print("No BLE devices found at all -- check that Bluetooth is enabled.")
        return 1
    devices.sort(key=lambda d: (d.name or "\xff").lower())
    hit = False
    for d in devices:
        name = d.name or "(no name)"
        marker = ""
        if d.name and "mecc" in d.name.lower():
            marker = "   <-- your Meccanoid!"
            hit = True
        print(f"  {d.address}  {name}{marker}")
    if not hit:
        print(
            "\nNo device advertising a Meccanoid-like name was seen. The robot\n"
            "only advertises while powered on and not already connected to\n"
            "something (e.g. the phone app). Power-cycle it and scan again."
        )
    return 0


# ----------------------------------------------------------------------
# explore

async def cmd_explore(args) -> int:
    address = await _resolve_address(args.address)
    if address is None:
        return 1
    print(f"Connecting to {address if isinstance(address, str) else address.address}...")
    async with BleakClient(address, timeout=args.timeout) as client:
        print("Connected. GATT table:\n")
        for service in client.services:
            print(f"service {service.uuid} (handle 0x{service.handle:04x})")
            for char in service.characteristics:
                props = ",".join(char.properties)
                print(f"  char 0x{char.handle:04x} {char.uuid} [{props}]")
        print(
            "\npymecca writes commands to the first match of: "
            "ffe9/ffe1 UUID, handle 0x001f, or any writable vendor "
            "characteristic. If your robot needs a different one, pass "
            "write_char=... to Meccanoid()."
        )
    return 0


# ----------------------------------------------------------------------
# demo

async def cmd_demo(args) -> int:
    address = await _resolve_address(args.address)
    if address is None:
        return 1
    print("Connecting (the robot should yawn and say \"I'm awake\")...")
    async with Meccanoid(address, write_char=args.write_char) as bot:
        print("Cycling eye colours...")
        for r, g, b in ((7, 0, 0), (0, 7, 0), (0, 0, 7), (7, 7, 0), (7, 0, 7), (0, 7, 7)):
            await bot.eye_lights(r, g, b)
            await asyncio.sleep(0.6)

        print("Waving arms...")
        for value in (0x00, 0xFF, 0x80):
            await bot.servo(protocol.Servo.LEFT_SHOULDER, value)
            await bot.servo(protocol.Servo.RIGHT_SHOULDER, value)
            await asyncio.sleep(1.0)

        print("Blinking chest lights...")
        for _ in range(2):
            for light in range(4):
                await bot.chest_light(light, True)
                await asyncio.sleep(0.15)
            for light in range(4):
                await bot.chest_light(light, False)
                await asyncio.sleep(0.15)

        if args.wheels:
            print("Wheel test: forward, back, spin...")
            await bot.drive(150, 150)
            await asyncio.sleep(1.0)
            await bot.drive(-150, -150)
            await asyncio.sleep(1.0)
            await bot.drive(150, -150)
            await asyncio.sleep(1.0)
            await bot.stop()

        await bot.eye_lights(0, 0, 7)
        print("Demo done.")
    return 0


# ----------------------------------------------------------------------
# drive (keyboard teleop)

_DRIVE_HELP = """\
Driving -- keys:
  w/s : forward / backward       a/d : turn left / right
  space : stop                   1-9 : set speed (x28)
  e : cycle eye colour           q : quit

Arms (this humanoid's observed slots):
  r/f : right shoulder up / down     t/g : left shoulder up / down
  y/h : right elbow front / back     u/j : left elbow front / back
  o   : right hand forward           p   : both arms up
"""


class _RawKeys:
    """
    Cross-platform single-keypress reader ('q', 'w', ...).
    """

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

    async def get(self) -> str:
        loop = asyncio.get_running_loop()
        if sys.platform == "win32":
            import msvcrt

            def read() -> str:
                ch = msvcrt.getch()
                return ch.decode(errors="ignore")

        else:

            def read() -> str:
                return sys.stdin.read(1)

        return await loop.run_in_executor(None, read)


async def cmd_drive(args) -> int:
    address = await _resolve_address(args.address)
    if address is None:
        return 1
    print("Connecting...")
    async with Meccanoid(address, write_char=args.write_char) as bot:
        print(_DRIVE_HELP)
        speed = 150
        eyes = [(7, 0, 0), (0, 7, 0), (0, 0, 7), (7, 7, 7)]
        eye_i = 2
        # Track logical arm positions so nudge keys can step from here.
        arms = {
            LEFT_SHOULDER_SLOT: 0x7F,
            LEFT_ELBOW_SLOT: 0x80,
            RIGHT_SHOULDER_SLOT: RIGHT_SHOULDER_CENTRE,
            RIGHT_ELBOW_SLOT: 0x80,
        }

        async def set_arm(slot: int, value: int, label: str) -> None:
            value = clamp_servo(value)
            arms[slot] = value
            await bot.servo(slot, value)
            print(f"{label} = 0x{value:02x}")

        async def nudge(slot: int, delta: int, label: str) -> None:
            await set_arm(slot, arms[slot] + delta, label)

        with _RawKeys() as keys:
            while True:
                key = (await keys.get()).lower()
                if key == "q":
                    await bot.stop()
                    break
                elif key == "w":
                    await bot.drive(speed, speed)
                elif key == "s":
                    await bot.drive(-speed, -speed)
                elif key == "a":
                    await bot.drive(-speed, speed)
                elif key == "d":
                    await bot.drive(speed, -speed)
                elif key == " ":
                    await bot.stop()
                elif key == "e":
                    eye_i = (eye_i + 1) % len(eyes)
                    await bot.eye_lights(*eyes[eye_i])
                elif key == "r":
                    # Right shoulder: toward up (0xff).
                    await nudge(RIGHT_SHOULDER_SLOT, ARM_NUDGE_STEP, "right shoulder")
                elif key == "f":
                    await nudge(RIGHT_SHOULDER_SLOT, -ARM_NUDGE_STEP, "right shoulder")
                elif key == "t":
                    # Left shoulder: toward up (0x00), so nudge decreases.
                    await nudge(LEFT_SHOULDER_SLOT, -ARM_NUDGE_STEP, "left shoulder")
                elif key == "g":
                    await nudge(LEFT_SHOULDER_SLOT, ARM_NUDGE_STEP, "left shoulder")
                elif key == "y":
                    # Right elbow: toward front (0x00).
                    await nudge(RIGHT_ELBOW_SLOT, -ARM_NUDGE_STEP, "right elbow")
                elif key == "h":
                    await nudge(RIGHT_ELBOW_SLOT, ARM_NUDGE_STEP, "right elbow")
                elif key == "u":
                    # Left elbow: toward front (0xff).
                    await nudge(LEFT_ELBOW_SLOT, ARM_NUDGE_STEP, "left elbow")
                elif key == "j":
                    await nudge(LEFT_ELBOW_SLOT, -ARM_NUDGE_STEP, "left elbow")
                elif key == "o":
                    await apply_right_hand_forward(bot)
                    arms[RIGHT_SHOULDER_SLOT] = RIGHT_SHOULDER_CENTRE
                    arms[RIGHT_ELBOW_SLOT] = RIGHT_ELBOW_FRONT
                    print("right hand forward")
                elif key == "p":
                    await apply_arms_up(bot)
                    arms[LEFT_SHOULDER_SLOT] = LEFT_SHOULDER_UP
                    arms[RIGHT_SHOULDER_SLOT] = RIGHT_SHOULDER_UP
                    print("arms up")
                elif key.isdigit() and key != "0":
                    speed = int(key) * 28
                    print(f"speed = {speed}")
    print("Bye.")
    return 0


# ----------------------------------------------------------------------
# repl

async def cmd_repl(args) -> int:
    address = await _resolve_address(args.address)
    if address is None:
        return 1
    print("Connecting...")
    async with Meccanoid(address, write_char=args.write_char) as bot:
        print(COMMAND_HELP)
        loop = asyncio.get_running_loop()
        while True:
            try:
                line = await loop.run_in_executor(None, input, "mecca> ")
            except (EOFError, KeyboardInterrupt):
                break
            result = await dispatch(bot, line)
            if result.outcome == CommandOutcome.QUIT:
                break
            if result.outcome == CommandOutcome.HELP:
                print(result.message)
            elif result.outcome == CommandOutcome.ERROR:
                print(format_reply(result))
            elif result.message:
                print(result.message)
    print("Bye.")
    return 0


# ----------------------------------------------------------------------
# session / do

def _session_dir(args) -> Path | None:
    raw = getattr(args, "session_dir", None)
    return Path(raw) if raw else None


async def cmd_session_start(args) -> int:
    directory = _session_dir(args)
    if session_is_live(directory):
        if not args.force:
            info = read_info(directory) or {}
            return _fail(
                f"a session is already running (pid {info.get('pid')}); "
                "use `pymecca session stop` or pass --force"
            )
        print("Stopping existing session (--force)...")
        stop_session(directory)

    cleanup_stale(directory)

    address = await _resolve_address(args.address)
    if address is None:
        return 1
    if not isinstance(address, str):
        address = address.address

    if args.foreground:
        server = SessionServer(
            address,
            write_char=args.write_char,
            directory=directory,
            connect_timeout=args.timeout,
        )
        await server.run()
        return 0

    # Re-invoke this process in the foreground, detached.
    argv = [
        sys.executable,
        "-m",
        "pymecca",
        "session",
        "start",
        "--foreground",
        "--timeout",
        str(args.timeout),
        address,
    ]
    if args.write_char is not None:
        argv.extend(["--char", str(args.write_char)])
    if directory is not None:
        argv.extend(["--session-dir", str(directory)])
    try:
        return spawn_background(argv, directory=directory)
    except Exception as e:
        return _fail(str(e))


def cmd_session_status(args) -> int:
    directory = _session_dir(args)
    if not session_is_live(directory):
        cleanup_stale(directory)
        print("No session running.")
        return 1
    info = read_info(directory) or {}
    print(f"pid:     {info.get('pid')}")
    print(f"address: {info.get('address')}")
    print(f"socket:  {info.get('socket')}")
    try:
        reply = send_command("ping", directory=directory)
        print(f"ping:    {reply}")
    except OSError as e:
        print(f"ping:    error: {e}")
        return 1
    return 0


def cmd_session_stop(args) -> int:
    directory = _session_dir(args)
    message = stop_session(directory)
    print(message)
    return 0


def cmd_do(args) -> int:
    directory = _session_dir(args)
    words = list(args.words)
    if words and words[0] == "--":
        words = words[1:]
    line = " ".join(words)
    if not line.strip():
        return _fail("empty command")
    if not session_is_live(directory):
        return _fail("no live session; run `pymecca session start` first")
    try:
        reply = send_command(line, directory=directory)
    except OSError as e:
        return _fail(str(e))
    print(reply)
    if reply.startswith("error"):
        return 1
    return 0


# ----------------------------------------------------------------------

def _write_char_arg(value: str):
    """
    A --char argument: either an integer handle (0x1f / 31) or a UUID.
    """
    try:
        return int(value, 0)
    except ValueError:
        return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pymecca",
        description="Control a Meccano Meccanoid G15/G15KS over Bluetooth LE.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scan", help="scan for BLE devices and spot the Meccanoid")
    p.add_argument("--timeout", type=float, default=10.0, help="scan seconds (default 10)")
    p.set_defaults(func=cmd_scan)

    def connect_args(p):
        p.add_argument("address", nargs="?", help="robot address (scans if omitted)")
        p.add_argument("--timeout", type=float, default=20.0, help="connect timeout")
        p.add_argument(
            "--char",
            dest="write_char",
            type=_write_char_arg,
            default=None,
            help="force the write characteristic (UUID or handle, e.g. 0x1f)",
        )

    p = sub.add_parser("explore", help="dump the robot's GATT services/characteristics")
    connect_args(p)
    p.set_defaults(func=cmd_explore)

    p = sub.add_parser("demo", help="connect and run a short demo")
    connect_args(p)
    p.add_argument("--wheels", action="store_true", help="also test the wheels (robot will move!)")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("drive", help="drive the robot with the keyboard (WASD)")
    connect_args(p)
    p.set_defaults(func=cmd_drive)

    p = sub.add_parser("repl", help="interactive command prompt")
    connect_args(p)
    p.set_defaults(func=cmd_repl)

    sess = sub.add_parser("session", help="manage a persistent BLE session")
    sess_sub = sess.add_subparsers(dest="session_command", required=True)

    def session_dir_arg(p):
        p.add_argument(
            "--session-dir",
            default=None,
            help="directory for socket/pid files (default: ~/.cache/pymecca)",
        )

    p = sess_sub.add_parser("start", help="connect and keep the BLE link open")
    connect_args(p)
    session_dir_arg(p)
    p.add_argument(
        "--foreground",
        action="store_true",
        help="run in this terminal instead of detaching to the background",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="stop an existing session before starting",
    )
    p.set_defaults(func=cmd_session_start)

    p = sess_sub.add_parser("status", help="show whether a session is running")
    session_dir_arg(p)
    p.set_defaults(func=cmd_session_status)

    p = sess_sub.add_parser("stop", help="disconnect and stop the session")
    session_dir_arg(p)
    p.set_defaults(func=cmd_session_stop)

    p = sub.add_parser("do", help="send one command to the live session")
    session_dir_arg(p)
    p.add_argument(
        "words",
        nargs="+",
        help="command line, e.g. raise right arm / eyes red",
    )
    p.set_defaults(func=cmd_do)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        func = args.func
        if inspect.iscoroutinefunction(func):
            return asyncio.run(func(args)) or 0
        return func(args) or 0
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except Exception as e:  # surface BLE errors tidily
        return _fail(str(e))


if __name__ == "__main__":
    sys.exit(main())
