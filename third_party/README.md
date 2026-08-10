# Third-party Meccanoid materials

Local mirrors and vendor copies kept for reverse-engineering and
documentation. Nothing here is part of the pymecca runtime.

| Path | Source | Notes |
|---|---|---|
| `revival/` | [MattimaxForce/Meccanoid-Revival](https://github.com/MattimaxForce/Meccanoid-Revival) | Smart Module PDF, official Arduino library zip, Revival README, construction manuals |
| `arduino/MeccanoidForArduino/` | [alexfrederiksen/MeccanoidForArduino](https://github.com/alexfrederiksen/MeccanoidForArduino) | Community Smart Module chain library (PWM daisy-chain, not BLE) |
| `arduino/MeccanoidHacks/` | [mrSiefen/MeccanoidHacks](https://github.com/mrSiefen/MeccanoidHacks) | Arduino / ROS hacks using that stack |
| `meblusy/` | [antoniolosada/MEBLUSY](https://github.com/antoniolosada/MEBLUSY) | Spanish GUI wrapping a vendored copy of original pymecca — **no extra BLE opcodes** |
| `apk/` | Neil Fraser / APKPure archive of `com.spinmaster.meccanoidrobot` | Stock Android app for APK reverse engineering; binary is gitignored (see `apk/README.md`) |
| `neil-fraser/` | [neil.fraser.name/software/meccanoid](https://neil.fraser.name/software/meccanoid/) | Firmware updater JSON catalogs; see [`docs/NEIL_FRASER.md`](../docs/NEIL_FRASER.md) for the full remote inventory |

See also:

* [`docs/NEIL_FRASER.md`](../docs/NEIL_FRASER.md) — Neil Fraser firmware / manual / APK archive map
* [`docs/SMART_MODULE_STACK.md`](../docs/SMART_MODULE_STACK.md) — catalog of the wired Smart Module protocol stack
* [`docs/UMPLESPLACE.md`](../docs/UMPLESPLACE.md) — community repair / app lore
* [`docs/MEBLUSY.md`](../docs/MEBLUSY.md) — opcode audit vs pymecca
* [`docs/SERVO_MAP.md`](../docs/SERVO_MAP.md) — live BLE behaviour map (`0x19`)

Legal: Spin Master / Meccano materials remain proprietary. They are archived
here for interoperability research only, not redistribution as a product.
