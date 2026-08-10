# umplesplace Meccanoid notes

Community repair / usage lore from
[umplesplace.wordpress.com](https://umplesplace.wordpress.com/), archived
under [`docs/reference/umplesplace/`](reference/umplesplace/).

These posts are **not** a BLE opcode map. They are useful for power,
firmware, app quirks, Robot vs Drone mode, and LIM behaviour.

Also mirrored: [Neil Fraser’s archive notes](NEIL_FRASER.md) (2021 firmware
updater post, 2016 workshop posts, firmware JSON catalogs).

## Post index

| Date | Title | Takeaways for pymecca |
|---|---|---|
| 2016-08-14 | [MeccAnnoyed](reference/umplesplace/2016-08-14-meccannoyed.md) | G15 4×C alkaline is weak; prefer **5S ~6.0 V NiMH** (KS pack chemistry). Do not use 6S. Tamiya connector on battery box; ~2.5 A polyfuse. Mentions FCC-leaked schematics. Firmware updater is essential. |
| 2016-10-12 | [New Meccanoid App](reference/umplesplace/2016-10-12-new-meccanoid-app.md) | Behavior Builder arrives; flash **G15 firmware 2.4** via Robot Updater (micro-USB). Works on G15 + 2.0. |
| 2016-10-16 | [G15 Brain Surgery](reference/umplesplace/2016-10-16-meccanoid-g15-brain-surgery.md) | Clock coin-cell / solder slag can stop the RTC; Behavior Builder uses the clock; hidden alarm in settings. MCU is a “black blob”. |
| 2017-04-02 | [G15 Dino](reference/umplesplace/2017-04-02-g15-dino.md) | **Drone mode** for non-humanoid builds; Robot mode expects stock servo layout and announces miswires. Buttons force listen mode if name recognition fails. Firmware **2.7** voice extras: “What time is it”, “Play a game”, “Dance with me”, “Hug me”. Battery display on app connect. G15 has more servo slots than 2.0 brain. |
| 2017-04-03 | [Bad Meccanoid Bad](reference/umplesplace/2017-04-03-bad-meccanoid-bad.md) | Voice **“Adjust Volume”** wrongly enters **Set Alarm**; setting alarm / LIM-for-alarm can brick LIM library until full wipe + reflash. Avoid. |
| 2017-06-22 | [G15X2-KS](reference/umplesplace/2017-06-22-meccanoid-g15x2-ks.md) | Firmware table by language (US **2.8** ahead of others). Volume workaround: flash UK 1.9, set volume, reflash 2.8. KS voice preferred. Servo part families: G15 “CAM 03” blue vs KS “DEV-06” yellow. |
| 2017-07-01 | [And then there's the App](reference/umplesplace/2017-07-01-and-then-theres-the-app.md) | Long app critique. Official Arduino lib ≠ open Meccabrain; **BLE protocol never published**. App is heavy Unity; Behavior Builder quirks; LIM ~15 clips × ~3 min; Drone mode needs ≥4 servos for some Behavior paths; preferred wiring often slots 1+3; no odometry — timed drive only. |

## Cross-checks against our live map

* **Name / listen mode** — umples: press chest buttons if name fails; eyes
  change for menu vs name listen. Our probes: blue eyes = name listen;
  `behaviour 0x0b` records name; `0x0c` offers default “Meccanoid”.
* **LIM** — umples: on-robot LIM library; teach UI. Our probes: `0x09`
  purple teach prompt (green/red/yellow/blue help); `0x17` spoken LIM menu.
* **Systems check** — umples mentions firmware “Systems Check”; we map
  that spoken routine to BLE `behaviour 0x0a`.
* **Power** — umples 5S NiMH advice matches our tethered ~6 V supply
  experiments (wiring still flaky on the battery contacts).

## What umplesplace does *not* give us

* No GATT UUIDs, no `0x19` argument table, no HCI traces.
* No confirmation of which app screens emit which BLE frames — that is
  why the archived APK + HCI snoop are next.
