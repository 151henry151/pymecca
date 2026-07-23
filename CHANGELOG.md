# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
