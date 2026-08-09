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
- `lower right arm` / logical `0x80`: centred (also the shoulder target for
  “hand out in front”).
- Further down was observed around `0x20`; full down toward `0x00`.

### Slot 3 — right elbow

- Logical `0x00`: forearm/hand toward the **front** of the robot.
- Toward logical `0xff`: forearm/hand toward the **back** of the robot.

### Slot 1 — left elbow

Sense is **opposite** the right elbow (mirrored):

- Logical `0xff`: forearm/hand toward the **front** of the robot.
- Logical `0x00`: forearm/hand toward the **back** of the robot.

## Confirmed poses

| Pose | Alias | Commands |
|---|---|---|
| Right hand out in front | `right hand forward` / `put right hand out in front` | `servo 2 0x80`, `servo 3 0x00` |
| Left hand out in front | `left hand forward` / `put left hand out in front` | `servo 0 0x80`, `servo 1 0xff` |
| Both arms up | `arms up` / `hands up` | `servo 0 0x00`, `servo 2 0xff` |
| Both arms down | `arms down` / `hands down` | `servo 0 0xff`, `servo 2 0x00` |

Notes: right shoulder at `0xff` is straight up, **not** “hand forward”.
Elbow must be `0x00` (front) with the shoulder centred for the forward pose.

`pymecca drive` also exposes these as keyboard teleop (`o` / `p`) plus
per-joint nudge keys (`r`/`f`, `t`/`g`, `y`/`h`, `u`/`j`).

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

## Behaviours / presets (`behaviour …`, opcode `0x19` = `MB_PlayPreset`)

Canned sounds and phrases live here — not free-form TTS. The stock app
names this opcode **`MB_PlayPreset`** (see [`APK_ANALYSIS.md`](APK_ANALYSIS.md)).
App frames are `0x19`, **preset index**, **sub** (usually `0`), then zeros
+ checksum. pymecca’s `behaviour ID` probes use index=`ID`, sub=`0`.

**Do not confuse** preset index `0x15` (PlayPreset → laser-ready tone on
this unit) with opcode **`0x15` `MB_PlayLIM`** (LIM playback), which is a
different command.

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
| `0x0e` | nudge-back | Rolls **backward** roughly ~1 foot (same distance scale as `0x0d`; no speech noted). |
| `0x0f` | turn-left-90 | Spins about **90° left** (counterclockwise) in place. |
| `0x10` | turn-right-90 | Spins about **90° right** (clockwise) in place (confirmed twice). |
| `0x11` | turn-right-180 | Spins about **180° clockwise** in place. |
| `0x12` | laser-ready / ?error | Same laser-ready cue (confirmed twice). |
| `0x13` | laser-ready / ?error | Same laser-ready cue. |
| `0x14` | laser-ready / ?error | Same laser-ready cue. |
| `0x15` | laser-ready / ?error | Same laser-ready / error tone as `0x01`–`0x04` (earlier “shutdown / eyes off” report was a mis-categorization; re-checked 2026-07-24). |
| `0x16` | laser-ready / ?error | Same laser-ready cue (confirmed twice). |
| `0x17` | lim-menu-voice | Spoken menu-style list (approx.): **Record LIM**, **LIM library**, **Choose settings**, **Go to settings**, **Help**, **Later**, **Main menu**. (Exact phrasing TBD if re-listened.) |
| `0x18` | laser-ready / ?error | Same laser-ready cue. |
| `0x19` | *(none)* | No audible/visible effect (tried twice; link still OK). |
| `0x1a` | *(none)* | No audible/visible effect (tried twice). |
| `0x1b` | laser-ready / ?error | Same laser-ready cue. |
| `0x1c` | *(none)* | No audible/visible effect (tried twice). |
| `0x1d` | laser-ready / ?error | **Single-arg** `behaviour 0x1d` = laser-ready (confirmed twice). The connect **wake** is different: seventeen `0x1d` payload bytes (`wake_frame()`), not yet re-probed here as a multi-arg command. |
| `0x1e` | *(none)* | No audible/visible effect. |
| `0x1f` | *(none)* | No audible/visible effect. |
| `0x20` | *(none)* | No audible/visible effect. |
| `0x21` | *(none)* | No audible/visible effect. |

Note: `0x01`–`0x04`, `0x08`, `0x12`–`0x16`, `0x18`, `0x1b`, and
single-arg `0x1d` all produce the **same** cue. Hypothesis: generic
**reject / unrecognized-command** tone — still a guess. `0x05`–`0x07` were
silent. No BLE PowerPreset ID found yet that powers the unit off; use the
physical switch.

### Batch probe `0x22`–`0x40` (2026-07-22)

Non-isolated batch of single-arg behaviours in that range produced **no
interesting motion or speech** on this unit (same “nothing” class as
`0x19`–`0x21`). Not worth re-probing one-by-one unless APK / HCI evidence
points at a specific ID.

### Still open

* Multi-arg `0x19` payloads other than the seventeen-`0x1d` wake frame
* Whether “laser-ready” IDs are really rejects vs a named SFX bank
* App-triggered behaviours not reachable as single-byte args
* A real BLE power-off / deep-sleep command (preset `0x15` is not it)

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
- 2026-07-22: `0x0e` = nudge-back (~1 foot).
- 2026-07-22: `0x0f` = turn-left-90 (CCW).
- 2026-07-22: `0x10` = turn-right-90 (CW).
- 2026-07-22: `0x11` = turn-right-180 (CW).
- 2026-07-22: `0x12`–`0x14` = laser-ready again.
- 2026-07-22: `0x15` recorded as shutdown (eyes off) — later corrected.
- 2026-07-22: `0x16` = laser-ready; `0x17` = lim-menu-voice list; `0x18` = laser-ready.
- 2026-07-24: Reclassify `0x15` as laser-ready / error tone (not power-off).
- 2026-08-09: Add left-hand-forward and both-arms-down pose rows (mirrored
  from confirmed right-hand / arms-up extremes on this build).
- 2026-07-22: `0x19`–`0x21` mostly silent; single-arg `0x1d` = laser-ready
  (wake frame is multi-`0x1d`); batch `0x22`–`0x40` no interesting effect.
- 2026-07-23: Confirmed pose “right hand out in front” =
  shoulder slot 2 `0x80` + elbow slot 3 `0x00` (not shoulder `0xff`).
