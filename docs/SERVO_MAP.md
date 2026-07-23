# Observed Meccanoid hardware map

Hardware notes for the robot at address `C4:BE:84:D8:D6:21`
(`MECCANOID 21D6D8`), recorded interactively with pymecca 2.1.x.

Covers arm servo slots, wheels, eye LEDs, and chest LEDs.

Left/right below are from the **robot's own perspective** (the robot's
right hand is on your left when you face it), unless noted otherwise.
Values are the logical positions sent through pymecca (`0x00` .. `0xff`,
`0x80` ≈ centre). The library may invert some channels on the wire via
`REVERSED_SERVOS` in `pymecca/protocol.py`; this table describes what
**you see** when you send those logical values.

The stock library names in `pymecca.Servo` do **not** all match this
build's wiring. Prefer the slot numbers in this table until the enum is
reconciled.

## Confirmed

| Slot | Library name (may be wrong) | Joint | Observed motion |
|---:|---|---|---|
| 0 | `UNKNOWN_0` | Left shoulder | Raises / lowers the left arm at the shoulder |
| 1 | `RIGHT_ELBOW` | Left elbow | See direction notes — sense is mirrored vs the right elbow |
| 2 | `RIGHT_SHOULDER` | Right shoulder | Raises / lowers the right arm at the shoulder |
| 3 | `LEFT_SHOULDER` | Right elbow | See direction notes |

## No servo motion

| Slot | Library name | Notes |
|---:|---|---|
| 4 | `LEFT_ELBOW` | No visible motion on repeated full-range writes (`0x00`↔`0xff`) |
| 5 | `UNKNOWN_5` | No visible motion on full-range writes |
| 6 | `UNKNOWN_6` | No visible motion on full-range writes |
| 7 | `UNKNOWN_7` | No visible motion on full-range writes |

On this humanoid build, only slots **0–3** appear wired to arm servos.

## Direction notes

### Slot 0 — left shoulder

- Toward logical `0x00`: arm **up** (pointing at the sky).
- Toward logical `0xff` / `0xe0`: arm **down**.

### Slot 2 — right shoulder

- `raise right arm` / logical `0xff`: arm **up** (pointing at the sky).
- `lower right arm` / logical `0x80`: centred.
- Further down was observed around `0x20`.

### Slot 3 — right elbow

- Logical `0x00`: forearm/hand toward the **front** of the robot.
- Toward logical `0xff`: forearm/hand toward the **back** of the robot.

### Slot 1 — left elbow

Sense is **opposite** the right elbow (mirrored):

- Logical `0xff`: forearm/hand toward the **front** of the robot.
- Logical `0x00`: forearm/hand toward the **back** of the robot.

To point both raised arms forward: `servo 2 0xff`, `servo 0 0x00`,
`servo 3 0x00`, `servo 1 0xff`.

## Wheels (`drive LEFT RIGHT`)

Command form: `pymecca do drive <left> <right>` with each speed in
`-255..255` (negative = reverse, `0` = that side stopped).

| Command arg | Side (robot's perspective) | Observed |
|---|---|---|
| First (`left`) | Left drive wheel | Motor runs; needs a stronger/longer pulse than the right before motion is obvious. One left-foot **roller** can stick and resist rolling even when the drive wheel turns. |
| Second (`right`) | Right drive wheel | Responds at modest speed; forward and reverse both confirmed (`drive 0 70`, `drive 0 -70`). |

Notes:

- `drive 60 60` first looked like “right only” because the left side was
  binding; both channels are live.
- Prefer short low-speed pulses while the robot is on a tethered power
  cable so it does not yank the cord.

## Eye lights (`eyes …`)

Named colours (`eyes red`, `eyes green`, …) and RGB triples (`eyes R G B`,
each channel `0..7`) both work. Observed cycle matched expectations:

`off` → `red` → `green` → `blue` → `yellow` → `magenta` → `cyan` → `white`

## Chest lights (`chest N on|off`)

Four fixed-colour LEDs across the chest. Index `N` is `0..3`. Positions
below are from the **robot's perspective**, listed right → left:

| Index | Colour | Position (robot's perspective) |
|---:|---|---|
| 0 | Blue | Furthest right |
| 1 | Red | Right-centre |
| 2 | Green | Left-centre |
| 3 | Yellow | Furthest left |

So left → right on the robot: yellow (3), green (2), red (1), blue (0).

## Behaviours / speech (`behaviour …`, opcode `0x19`)

Canned sounds and phrases live here — not free-form TTS. Frames are
`0x19` plus up to 17 argument bytes (see `pymecca.protocol.behaviour_frame`).

### Voice UI (on-robot, not BLE)

With **blue eyes**, the Meccabrain is in name-listening mode. It periodically
prompts along the lines of: remember, when my eyes are blue, I'm listening
for my name — then plays the **recorded wake-word name**. That name is set
via behaviour **`0x0b`** (interactive mic recording + yellow to confirm),
not by sending raw audio over BLE from pymecca. Saying the name (or using
the front buttons / app) is how you interact with listening mode; BLE can
still work while eyes are blue if nothing else holds the link.

### Known (isolated probes)

Probe protocol: send **one** `behaviour` ID, wait for a human report, then
document before sending the next.

| ID | Nickname | Observed |
|---:|---|---|
| `0x01` | laser-ready / ?error | Same SFX as `0x02`–`0x04` |
| `0x02` | laser-ready / ?error | “Pzooow” + “bedoop” chirp |
| `0x03` | laser-ready / ?error | Same as above |
| `0x04` | laser-ready / ?error | Same as above |
| `0x05` | *(none)* | No audible/visible effect (tried twice) |
| `0x06` | *(none)* | No audible/visible effect |
| `0x07` | *(none)* | No audible/visible effect |
| `0x08` | laser-ready / ?error | Same laser-ready cue as `0x01`–`0x04` |
| `0x09` | lim-teach-prompt | Eyes go **purple**; spoken button help: **green** = go forward, **red** = go back, **yellow** = save, **blue** = exit. After a long pause: **“exiting to main menu”**, eyes **green**. Likely enters (then times out of) a L.I.M. / teach mode. |
| `0x0a` | systems-check | Full self-test routine. Spoken outline: **“Initiating system check. Reading battery level. Battery, full charge. Testing motor functions. Stand back!”** then drive: reverse, forward, turn right, turn left; **“performance optimal”** (or “functional”); **“testing servo functions”** + arm motion; further line(s); **“testing metabrain”** + ding; **“systems check 100% returning to main menu”**; eyes **green**. (This was the long routine from the earlier non-isolated sweep.) |
| `0x0b` | set-name | Interactive **name recording** routine. Prompts to set the name after a beep; records spoken name; plays back **“my name is …”** using the recording; asks for confirmation; **yellow** button confirms; announces name has been set. (This unit was renamed from “Hunter” to “Robot” during probing.) |
| `0x0c` | default-name-prompt | Asks whether to use the default name **“Meccanoid”**: *“Name robot: would you like to use my default name, Meccanoid? Press yellow button for yes, or blue button for no.”* Eyes **purple**; yellow/blue buttons blink while waiting; times out back to **blue** eyes if no press. |
| `0x0d` | nudge-forward | Rolls **forward** roughly ~1 foot (no speech noted). |
| `0x1d` | wake | Connect wake / “I'm awake”-style greeting family (seventeen `0x1d` bytes on connect) |

Note: `0x01`–`0x04` and `0x08` all produce the **same** cue. Hypothesis: this
may be a generic **reject / unrecognized-command** tone — unproven until a
clearly different ID (e.g. wake `0x1d`) is contrasted in the same session.
`0x05`–`0x07` were silent.

### 2026-07-22 rapid sweep (IDs not yet isolated)

Earlier non-isolated burst mixed several IDs; the spoken systems-check is
now attributed to **`0x0a`**. Remaining IDs from that burst (`0x10`,
`0x15`, `0x1a`, …) still need isolated probes. Lights-out after the first
run was likely loose power wiring, not this command.

## How to extend this map

With a live session:

```bash
pymecca session start
pymecca do servo N 0x20
# pause, observe
pymecca do servo N 0xe0
```

Update this file when a slot's joint and direction are confirmed. Date
new findings under [Changelog](#changelog) below.

## Changelog

- 2026-07-22: Initial map from interactive probing (slots 0–3 confirmed;
  slots 4–7 no servo motion; both drive channels confirmed; left foot
  roller can bind; eye colours confirmed; chest LEDs 0–3 mapped
  blue/red/green/yellow right→left).
- 2026-07-22: Record shoulder up/down extremes; left elbow front/back is
  mirrored vs right elbow (`0xff` = front on the left, `0x00` = front on
  the right).
- 2026-07-22: Behaviour sweep produced spoken “initiating systems check”,
  clockwise spin, then apparent shutdown; IDs not yet isolated.
- 2026-07-22: Isolated `0x01`–`0x03` all play the same laser-ready SFX
  (“pzooow” + “bedoop”); confirmed back-to-back.
- 2026-07-22: `0x05`–`0x07` silent; `0x08` laser-ready again; `0x09`
  purple-eyes L.I.M./teach prompt then “exiting to main menu” / green eyes.
- 2026-07-22: `0x0a` = full systems-check (battery, motors, servos,
  metabrain; ends “systems check 100% returning to main menu”).
- 2026-07-22: `0x0b` = set-name (record wake word; yellow confirms).
- 2026-07-22: `0x0c` = default-name-prompt (“Meccanoid?”; yellow=yes, blue=no).
- 2026-07-22: `0x0d` = nudge-forward (~1 foot).
