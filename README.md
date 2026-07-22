# pymecca

**Unofficial** Python library for controlling the Meccano **Meccanoid G15 / G15KS**
robot over Bluetooth LE.

This is a modernised rewrite of the original 2017 `pymecca` script. The old
version depended on Python 2 and BlueZ's long-removed `gatttool`, so it no
longer runs on any current system. This version is:

* **Python 3.9+** and fully type-hinted
* built on [bleak](https://github.com/hbldh/bleak), so it runs on **Linux
  (including Raspberry Pi), macOS and Windows** — control the robot from your
  laptop or a Pi, whichever you like
* **async-first** with a drop-in **blocking API** (`pymecca.sync`) for simple
  scripts and REPL tinkering
* self-configuring: it discovers the robot's GATT write characteristic at
  connect time instead of hardcoding a handle
* shipped with a **CLI**: scan for the robot, run a demo, drive it with WASD
  keys, poke the protocol interactively
* unit-tested (the protocol layer needs no robot to test)

👉 **New here? Read [GUIDE.md](GUIDE.md) for step-by-step setup with your robot.**

## Install

```bash
pip install git+https://github.com/151henry151/pymecca
# or from a clone:
pip install .
```

## Quick start

Find your robot (turn it on first, and make sure the phone app is *not*
connected to it):

```bash
pymecca scan
```

Run the built-in demo (eyes, arms, chest lights — add `--wheels` to test
driving):

```bash
pymecca demo            # auto-discovers the robot
pymecca drive           # WASD keyboard driving
pymecca repl            # interactive protocol prompt
pymecca explore         # dump the robot's GATT table (troubleshooting)
```

From Python, async:

```python
import asyncio
from pymecca import Meccanoid, Servo

async def main():
    async with Meccanoid("C4:BE:84:D4:68:1B") as bot:   # your robot's address
        await bot.eye_lights(7, 0, 0)                   # red eyes
        await bot.servo(Servo.RIGHT_SHOULDER, 0xFF)     # raise the right arm
        await bot.drive(150, 150)                       # roll forward
        await asyncio.sleep(1)
        await bot.stop()

asyncio.run(main())
```

Or blocking, no asyncio required:

```python
from pymecca.sync import Meccanoid

with Meccanoid("C4:BE:84:D4:68:1B") as bot:
    bot.eye_lights(0, 7, 0)
    bot.chest_light(0, True)
```

## API overview

| Method | What it does |
|---|---|
| `drive(left, right)` | wheel speeds, −255…255 (negative = backwards) |
| `stop()` | stop both wheels |
| `servo(Servo.X, 0..255)` | move a joint (`0x80` = centred) |
| `servo_light(n, "red")` | a servo's LED colour (8 colours) |
| `chest_light(n, True)` | chest LEDs 0–3 on/off |
| `eye_lights(r, g, b)` | eye colour, each channel 0–7 |
| `behaviour(...)` | raw opcode-`0x19` behaviours/sounds (experiment!) |
| `send_raw(frame)` | send any frame built with `pymecca.protocol` |

The wire protocol itself (frame format, checksum, opcodes) lives in
[`pymecca/protocol.py`](pymecca/protocol.py) as pure, dependency-free,
unit-tested functions — see its docstring for what is known about the
protocol.

## Development

```bash
pip install -e ".[dev]"
pytest          # protocol tests, no robot needed
ruff check .    # lint
```

## Credits and status

This is an unofficial, unsanctioned API for the Meccanoid, based on the
community's reverse engineering of its Bluetooth protocol. It began as
[iamsrp/pymecca](https://github.com/iamsrp/pymecca); the protocol knowledge
(opcodes, checksum, the "I'm awake" greeting) is inherited from that work.
Apache 2.0 licensed.
