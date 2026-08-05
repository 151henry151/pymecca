# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add observed hardware map for this Meccanoid (`docs/SERVO_MAP.md`): arm servo slots, wheels, eye colours, and chest LED positions
- Add umplesplace Meccanoid lore archive and summary (`docs/UMPLESPLACE.md`, `docs/reference/umplesplace/`)
- Add Smart Module / Arduino stack catalog (`docs/SMART_MODULE_STACK.md`) and mirror source trees under `third_party/`
- Add MEBLUSY opcode audit (`docs/MEBLUSY.md`); confirm no BLE opcodes beyond classic pymecca
- Add archived Android APK fetch helper (`third_party/apk/`) for reverse engineering
- Mirror Meccanoid-Revival assets (Smart Module PDF, official library, construction manuals)
- Add stock APK reverse-engineering notes (`docs/APK_ANALYSIS.md`): official `MB_Commands` opcode map, GATT `FFF0`/`FFF1`/`FFF2`, PlayPreset vs PlayLIM

### Changed

- Record mirrored left/right elbow front/back sense and shoulder up/down extremes in the hardware map
- Add initial opcode-`0x19` behaviour probing notes (systems-check speech; shutdown risk)
- Map isolated behaviour IDs `0x01`–`0x03` as the same laser-ready SFX
- Map behaviour `0x09` as L.I.M./teach prompt (purple eyes; green/red/yellow/blue button help)
- Map behaviour `0x0a` as the full spoken systems-check routine
- Map behaviour `0x0b` as the interactive set-name / wake-word recording routine
- Map behaviour `0x0c` as the default-name (“Meccanoid”) yes/no prompt
- Map behaviour `0x0d` as a short forward drive nudge
- Map behaviour `0x0e` as a short backward drive nudge
- Map behaviour `0x0f` as an in-place ~90° left / counterclockwise turn
- Map behaviour `0x10` as an in-place ~90° right / clockwise turn
- Map behaviour `0x11` as an in-place ~180° clockwise turn
- Map behaviour `0x12`–`0x14` as the same laser-ready / possible-error cue
- Map behaviour `0x15` as shutdown (eyes off)
- Map behaviour `0x16` as laser-ready; `0x17` as LIM menu voice list; `0x18` as laser-ready
- Map behaviour `0x19`–`0x21` and batch `0x22`–`0x40` as no interesting effect; note single-arg `0x1d` vs multi-`0x1d` wake

## [2.1.0] - 2026-07-22

### Added

- Add a persistent BLE session (`pymecca session start|status|stop`) that keeps one Bluetooth connection open and accepts commands over a local Unix socket
- Add `pymecca do` to send a single command to the live session without reconnecting
- Extract a shared command dispatcher used by `repl` and the session server
- Add plain-English command aliases such as `raise right arm`, `lower the left arm`, and `eyes red`

## [2.0.0] - 2026-07-22

### Changed

- Rewrite the library for Python 3.9+ using bleak instead of Python 2 and gatttool
- Discover the GATT write characteristic at connect time
- Ship async and blocking client APIs, a CLI, and protocol unit tests
