# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add observed hardware map for this Meccanoid (`docs/SERVO_MAP.md`): arm servo slots, wheels, eye colours, and chest LED positions

### Changed

- Record mirrored left/right elbow front/back sense and shoulder up/down extremes in the hardware map
- Add initial opcode-`0x19` behaviour probing notes (systems-check speech; shutdown risk)
- Map isolated behaviour IDs `0x01`–`0x03` as the same laser-ready SFX
- Map behaviour `0x09` as L.I.M./teach prompt (purple eyes; green/red/yellow/blue button help)
- Map behaviour `0x0a` as the full spoken systems-check routine
- Map behaviour `0x0b` as the interactive set-name / wake-word recording routine
- Map behaviour `0x0c` as the default-name (“Meccanoid”) yes/no prompt
- Map behaviour `0x0d` as a short forward drive nudge

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
