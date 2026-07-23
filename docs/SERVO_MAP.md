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
