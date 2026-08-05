# Getting your Meccanoid G15 working with pymecca

This guide takes you from a robot in a box to driving it from Python, on a
laptop (Linux / macOS / Windows) or a Raspberry Pi. It also covers what to do
when things don't work, which with 10-year-old toy Bluetooth hardware is a
real possibility.

## 1. What you need

* A **Meccanoid G15 or G15KS** with the **Meccabrain** module installed and
  its servos plugged in (the standard humanoid build).
* **Fresh or fully charged batteries.** This is not a throwaway tip: a weak
  battery pack is the single most common cause of flaky Bluetooth on these
  robots — the radio browns out before the motors visibly do. If connections
  drop randomly, change the batteries first.
* A computer with **Bluetooth LE (Bluetooth 4.0+)**:
  * Any Raspberry Pi 3/4/5 or Zero W/2W (built-in BLE), or
  * basically any laptop from the last decade, or a ~$10 USB BLE dongle.
* **Python 3.9 or newer.**

You do **not** need the Meccanoid phone app, and you do not need to "pair"
the robot in your OS Bluetooth settings — BLE connections here are made
directly by the library, unpaired.

## 2. Install pymecca

### Linux / Raspberry Pi (Raspberry Pi OS, Debian, Ubuntu…)

```bash
sudo apt update
sudo apt install python3-pip bluez     # bluez is preinstalled on Pi OS
pip3 install git+https://github.com/151henry151/pymecca
```

Notes:

* On recent OS versions, `pip3 install` may refuse to install system-wide
  ("externally managed environment"). Use a virtual environment:

  ```bash
  python3 -m venv ~/mecca-env
  ~/mecca-env/bin/pip install git+https://github.com/151henry151/pymecca
  source ~/mecca-env/bin/activate      # then `pymecca ...` works
  ```

* You should *not* need `sudo` to scan or connect on a modern BlueZ. If
  scanning only works as root, either run once with `sudo` or grant Python
  the capability: check that your user is in the `bluetooth` group
  (`sudo usermod -aG bluetooth $USER`, then log out/in).

### macOS

```bash
pip3 install git+https://github.com/151henry151/pymecca
```

The first time you scan, macOS will ask to give your terminal **Bluetooth
permission** (System Settings → Privacy & Security → Bluetooth). Say yes.
One quirk: macOS hides real MAC addresses, so `pymecca scan` will show a
long UUID instead — that UUID *is* the address, use it wherever this guide
says "address".

### Windows 10/11

```powershell
pip install git+https://github.com/151henry151/pymecca
```

Needs Windows 10 build 16299 or later (any updated Win10/11 is fine) and
Bluetooth turned on in Settings.

## 3. Get the robot ready

1. Build state doesn't matter much, but the **Meccabrain must be powered**
   and the servos plugged into its ports for arm control to work.
2. Turn the robot **on**.
3. **Make sure nothing else is connected to it.** The Meccabrain accepts one
   Bluetooth connection at a time — if the Meccanoid phone app (or a
   previously-paired phone in range) is connected, your computer will never
   see it. Force-close the app / turn off the phone's Bluetooth while
   testing.
4. If in doubt, power-cycle the robot right before scanning. It advertises
   over BLE whenever it's on and unconnected.

## 4. Find it

```bash
pymecca scan
```

You should see a list of BLE devices, with your robot flagged:

```
  C4:BE:84:D4:68:1B  MECCANOID12345   <-- your Meccanoid!
```

Write that address down — commands accept it, and it never changes (except
on macOS, where the UUID shown is stable per-computer).

If it doesn't show up, see [Troubleshooting](#7-troubleshooting).

> Pi/Linux alternative if you want a second opinion: `bluetoothctl scan le`
> shows raw advertisements. (The old `hcitool lescan` from the original
> README is deprecated but usually still present.)

## 5. First contact

```bash
pymecca demo C4:BE:84:D4:68:1B     # or just `pymecca demo` to auto-discover
```

On connect the robot should **yawn and say "I'm awake"**, then cycle its eye
colours, wave its arms, and blink the chest LEDs. That yawn is your
confirmation that command writes are actually reaching the robot. Add
`--wheels` if you also want it to roll forward/back/spin (give it floor
space).

Then have some real fun:

```bash
pymecca drive      # drive with W/A/S/D, space = stop, e = eye colour, q = quit
pymecca repl       # type protocol commands interactively, e.g.:
                   #   eyes 7 0 0
                   #   servo 2 255
                   #   drive 150 150
                   #   stop
```

The `repl` is the best tool for learning what your robot's servo numbers and
directions actually are — move things one at a time and watch.

## 6. Keep a persistent Bluetooth session

Each one-shot command (`demo`, a short script, etc.) connects, acts, then
disconnects. The robot announces that, and reconnects can be flaky. For a
string of commands, start a session once and talk to it with `pymecca do`:

```bash
pymecca session start C4:BE:84:D4:68:1B   # or omit the address to auto-scan
pymecca session status

pymecca do raise right arm
pymecca do lower right arm
pymecca do eyes red
pymecca do servo 2 128
pymecca do stop

pymecca session stop
```

The session process holds the BLE link and listens on a Unix socket under
`~/.cache/pymecca/` (override with `--session-dir`). `pymecca do` is a
short-lived client: it sends one line and exits; the robot stays connected.

Useful aliases (also work in `repl`):

* `raise right arm` / `lower right arm` (and left; optional `the`)
* `eyes red|green|blue|white|off|yellow|magenta|cyan`

By default `session start` detaches to the background and logs to
`~/.cache/pymecca/session.log`. Pass `--foreground` to keep it in the
terminal. If a session is already running, `--force` replaces it.

## 7. Write your own programs

Async (recommended for anything real):

```python
import asyncio
from pymecca import Meccanoid, Servo

async def main():
    async with Meccanoid("C4:BE:84:D4:68:1B") as bot:
        await bot.eye_lights(7, 0, 7)              # magenta eyes
        await bot.servo(Servo.LEFT_SHOULDER, 0x00) # arm up
        await asyncio.sleep(1)
        await bot.servo(Servo.LEFT_SHOULDER, 0x80) # centred again

asyncio.run(main())
```

Blocking (nice for the REPL and quick scripts):

```python
from pymecca.sync import Meccanoid
bot = Meccanoid("C4:BE:84:D4:68:1B")
bot.connect()
bot.eye_lights(0, 7, 7)
bot.drive(100, 100); import time; time.sleep(1); bot.stop()
bot.disconnect()
```

What's controllable:

| Thing | Call | Range |
|---|---|---|
| Wheels | `drive(left, right)` | −255…255 each, negative = reverse |
| Arm joints | `servo(Servo.RIGHT_ELBOW, v)` | 0–255, 128 = centre |
| Servo LEDs | `servo_light(n, "cyan")` | 8 colours (3-bit RGB) |
| Eyes | `eye_lights(r, g, b)` | 0–7 per channel |
| Chest LEDs | `chest_light(n, True)` | 4 individual LEDs |
| Sounds/behaviours | `behaviour(0x1d, ...)` | mostly unmapped — explore! |

The stock build uses servos 1–4 (`RIGHT_ELBOW`, `RIGHT_SHOULDER`,
`LEFT_SHOULDER`, `LEFT_ELBOW`). Two of them are mounted mirrored;
the library un-mirrors them for you so 0→255 sweeps every joint in a
consistent direction.

See `examples/` for complete runnable scripts.

## 8. Troubleshooting

**`pymecca scan` shows nothing at all.**
Bluetooth is off, or (Linux) the adapter is down (`sudo hciconfig hci0 up` /
`rfkill unblock bluetooth`), or (macOS) the terminal lacks Bluetooth
permission, or (Linux) you need to be in the `bluetooth` group. Verify the
adapter works by scanning with your phone nearby — you should at least see
*something*.

**Scan works, but no Meccanoid appears.**
In order of likelihood: the phone app (or a phone that has auto-reconnected)
is hogging the connection; the robot is off or asleep; the batteries are
weak; you're out of range (BLE on this toy is ~10 m line-of-sight).
Power-cycle the robot and scan again immediately.

**It connects, but nothing happens (no yawn, no lights).**
The commands are landing on the wrong GATT characteristic. Run:

```bash
pymecca explore <address>
```

and look at the printed table. pymecca auto-picks, in order: a `ffe9` or
`ffe1` vendor characteristic, then ATT handle `0x001f` (what the original
2017 library hardcoded), then any writable vendor characteristic. If your
firmware differs, force one:

```bash
pymecca demo <address> --char 0x1f          # by handle
pymecca demo <address> --char 0000ffe9-0000-1000-8000-00805f9b34fb   # by UUID
```

(or `Meccanoid(address, write_char=0x1f)` in code). If you find a firmware
that needs this, please open an issue with your `explore` output so the
default list can be extended.

**It connects, then drops after a few seconds.**
Almost always battery. Otherwise: move closer, and on the Pi avoid heavy
2.4 GHz Wi-Fi traffic at the same moment (shared radio on Pi 3/Zero).

**`ImportError: No module named bleak` under sudo.**
`sudo python3` uses root's packages, not your venv's. Prefer running
unprivileged; if you must use sudo, `sudo ~/mecca-env/bin/python your.py`.

**Servo moves the "wrong" way.**
Servo direction depends on how each servo was physically assembled into the
model. Use `pymecca repl` to test each joint; if one is inverted on your
build, just send `255 - value` for that joint in your code.

**`pymecca do` says there is no live session.**
Start one with `pymecca session start` (robot on, phone app not connected).
Check `pymecca session status`. Look at `~/.cache/pymecca/session.log` if a
background start failed.

## 9. How the protocol works (for the curious)

Every command is a 20-byte BLE write: 18 command bytes followed by a 16-bit
big-endian checksum (the plain sum of the 18 bytes). The first byte is an
opcode: `0x08` servos, `0x0C` servo LEDs, `0x0D` wheels, `0x11` eyes,
`0x19` behaviours/sounds, `0x1C` chest LEDs. Servo and LED commands always
carry *all eight* slots, so the library remembers the last state and mutates
it. None of this is official — it's community reverse engineering, inherited
from the original pymecca and preserved (with tests) in
[`pymecca/protocol.py`](pymecca/protocol.py).

There is plenty left to discover — in particular the `0x19` behaviour space
(sounds, built-in animations) is nearly unmapped. `pymecca repl`'s
`behaviour` and `raw` commands are your laboratory. Have fun!
