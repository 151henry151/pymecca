# Smart Module stack (wired, not BLE)

This documents the **different stack** from phone BLE: the MeccaBrain ↔
Smart Servo / Smart LED daisy-chain on a single data wire. Useful when
bypassing the Meccabrain with Arduino, or when reading official PDFs.
It does **not** describe the BLE frames pymecca sends (`0x08`, `0x19`, …).

## Sources mirrored here

| Artifact | Location |
|---|---|
| Official protocol PDF (2015) | [`third_party/revival/Meccano_SmartModuleProtocols_2015.pdf`](../third_party/revival/Meccano_SmartModuleProtocols_2015.pdf) |
| Official Arduino API (`MeccaBrain.cpp` / `.h`) | [`third_party/revival/meccanoid-library/`](../third_party/revival/meccanoid-library/) |
| Community library (preferred by hackers) | [`third_party/arduino/MeccanoidForArduino/`](../third_party/arduino/MeccanoidForArduino/) |
| Example sketches / ROS notes | [`third_party/arduino/MeccanoidHacks/`](../third_party/arduino/MeccanoidHacks/) |
| Construction manuals from Revival | [`third_party/revival/15401b.pdf`](../third_party/revival/15401b.pdf), [`15402b.pdf`](../third_party/revival/15402b.pdf) |

Upstream links:

* [MattimaxForce/Meccanoid-Revival](https://github.com/MattimaxForce/Meccanoid-Revival)
* [alexfrederiksen/MeccanoidForArduino](https://github.com/alexfrederiksen/MeccanoidForArduino)
* [mrSiefen/MeccanoidHacks](https://github.com/mrSiefen/MeccanoidHacks)
* Companion blog: [Meccanoid Hacks Part 1](https://mrsiefensrobotemporium.com/blogs/2022/October/meccanoidHackspt1.html)

## Hardware picture (from the 2015 PDF)

* **MeccaBrain**: MCU, 4 lit buttons, speaker, mic, BLE to the phone app,
  ON/OFF + **ROBOT/DRONE** switch, LM/RM H-bridges for foot DC motors
  (not Smart Modules), micro-USB for firmware updater, **8 Smart Module
  channels** (max 4 modules daisy-chained per channel; practical servo
  limit ~16 from power).
* **Smart Servo**: angle + LIM (limp / encoder feedback) + RGB LED +
  clutch / stall protection; input + output plugs for chaining.
* **Smart LED**: dual RGB eyes, fade time; **end of chain only** (no
  output plug). Needs **two** data packets to update (9-bit colour +
  3-bit fade).

Wiring per module: white = bidirectional data, red = 5 V, black = GND.
A pull-up circuit is required when talking from a bare MCU (see PDF).

## Packet format (MeccaBrain → modules)

Each channel emits 6-byte packets:

```text
{0xFF, Data1, Data2, Data3, Data4, Checksum/ModuleID}
```

* Header is always `0xFF` (forbidden elsewhere).
* `DataN` is for daisy-chain position N (1 = nearest the brain).
* Last byte: high nibble = checksum over the four data bytes; low nibble
  = which module should reply this round (round-robin).
* Bit timing from brain: ~417 µs/bit, start low + two stop highs; bits
  sent LSB-first.

Reserved data values:

| Byte | Meaning |
|---:|---|
| `0xFE` | No module / ID not assigned |
| `0xFD` | Erase ID |
| `0xFC` | Report module type |
| `0xFB` | Reserved |
| `0x01` | Module type: Smart Servo |
| `0x02` | Module type: Smart LED |

Discovery: brain sends all `0xFE`, first module claims a slot, brain then
sends `0xFC` to learn type, then normal data.

## Packet format (modules → MeccaBrain)

One reply byte per brain packet, from the module named in the ID nibble.
Module bit timing is slower (~1.1 ms/bit, ~2 ms start low); encoding is
pulse-width based (high pulse ≷ 400 µs for 1/0). Constant LOW ⇒ unplugged.

## Official library vs MeccanoidForArduino

* **Official `MeccaBrain` class**: bit-bangs one PWM pin; methods for LED
  colour, servo position, LIM, communicate/checksum. Header carries a
  Spin Master proprietary notice — free to use with Meccano hardware,
  **not** open-source licensing of the Meccabrain firmware itself.
* **MeccanoidForArduino**: cleaner `Chain` / `MeccanoServo` / `MeccanoLed`
  API; auto-update after property sets; same 4-module-per-chain limit;
  recommended by MeccanoidHacks over the official zip (“has typos”).
* **MeccanoidHacks**: example `.ino` sketches; notes that G15 / 2.0 /
  G15KS / 2.0XL are all Arduino-hackable on this wired path.

## Relation to pymecca BLE

Phone BLE talks to the **Meccabrain firmware**, which then drives Smart
Modules and foot motors. Arduino on a channel **replaces** that path for
those modules. BLE opcodes (`0x08` servo frame, `0x19` behaviours, …)
and Smart Module bytes (`0xFF` header packets) are different layers —
do not confuse them when reading captures.
