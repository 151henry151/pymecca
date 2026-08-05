# Stock Android APK analysis

APK: `com.spinmaster.meccanoidrobot` **4.02** (versionCode 48), fetched via
[`third_party/apk/fetch-apk.sh`](../third_party/apk/fetch-apk.sh).

Decompile artifacts are local-only (gitignored): `third_party/apk/jadx-out/`,
`third_party/apk/csharp-il/`, `third_party/apk/tools/`.

## App shape

Unity (Mono) game with a thin Android BLE plugin:

| Layer | Location |
|---|---|
| Java BLE bridge | `com.shatalmic.unityandroidbluetoothlelib.UnityBluetoothLE` |
| Unity BLE API shim | `Assembly-CSharp-firstpass` → `BluetoothLEHardwareInterface` |
| Protocol / robot control | `Assembly-CSharp` → class **`BluetoothLE`** |
| UI glue | `BLEManager` |

Protocol lives in C#, not in jadx Java output.

## GATT UUIDs (from `BluetoothLE` ctor)

| Role | Short UUID |
|---|---|
| Service | `FFF0` |
| Notify / subscribe | `FFF1` |
| Write | `FFF2` |

Full form: `0000fffN-0000-1000-8000-00805f9b34fb`.

pymecca historically preferred `ffe9` / `ffe1` (older Bluegiga-style
candidates). Discovery by “any writable vendor characteristic” still
works when `FFF2` is present; prefer adding `FFF2` to the candidate list.

## Frame format

Every write is a **20-byte** buffer: 18 payload bytes + 2 checksum bytes
(matches pymecca `COMMAND_LENGTH = 18`).

Checksum (`BluetoothLE.calculateChecksum`):

1. Sum bytes `[0 .. len-3]` (all but the last two).
2. Store `(sum >> 8) & 0xff` at index `len-2`.
3. Store `sum & 0xff` at index `len-1`.

## Official opcode enum (`BluetoothLE.MB_Commands`)

Extracted from `Assembly-CSharp.dll` IL:

| Opcode | Name | Notes |
|---:|---|---|
| `0x01` | `MB_Status` | Status request / report |
| `0x02` | `MB_GetConfig1` | |
| `0x03` | `MB_GetConfig2` | |
| `0x04` | `MB_SetConfig1` | |
| `0x05` | `MB_Setconfig2` | |
| `0x06` | `MB_SetName` | BLE name set (distinct from on-robot voice name UI) |
| `0x07` | `MB_GetName` | |
| `0x08` | `MB_SetServoPos` | pymecca servo frame |
| `0x09` | `MB_GetServoPos` | |
| `0x0A` | `MB_GetServoStatus` | |
| `0x0B` | `MB_SetServoStatus` | |
| `0x0C` | `MB_SetServoLED` | pymecca servo lights |
| `0x0D` | `MB_SetMotorValues` | pymecca drive |
| `0x0E` | `MB_GetMotorValues` | |
| `0x0F` | `MB_GetRGBLEDColor1` | |
| `0x10` | `MB_GetRGBLEDColor2` | |
| `0x11` | `MB_SetRGBLEDColor1` | pymecca eye lights |
| `0x12` | `MB_SetRGBLEDColor2` | |
| `0x13` | `MB_GetLIMInfo` | |
| `0x14` | `MB_ChangeLIMName` | |
| `0x15` | `MB_PlayLIM` | **LIM playback** (opcode, not a preset ID) |
| `0x16` | `MB_RecordLIM` | |
| `0x17` | `MB_DeleteLIM` | |
| `0x18` | `MB_GetPresetInfo` | |
| `0x19` | `MB_PlayPreset` | What pymecca calls `behaviour` |
| `0x1A` | `MB_SendPinNumber` | App `SendPIN()` |
| `0x1B` | `MB_SetTimeAndDate` | |
| `0x1C` | `MB_SetPCBLED` | pymecca chest lights |
| `0x1D` | `MB_GetTimeAndDate` | |
| `0x1E` | `MB_GetServoLED` | |
| `0x1F` | `MB_SetServoMapping` | |
| `0x20` | `MB_GetServoMapping` | |

## `0x19` PlayPreset (our “behaviour” probes)

App method `playPreset(uint8 index, uint8 sub = 0, bool immediatePlay = false)`:

```text
buf[0] = 0x19
buf[1] = index
buf[2] = sub
buf[3..17] = 0
checksum → buf[18], buf[19]
```

Our isolated probes used `index = ID`, `sub = 0`. That maps the live
table in [`SERVO_MAP.md`](SERVO_MAP.md) onto **preset IDs**, not onto
other opcodes. Important corrections:

* CLI `behaviour 0x15` = PlayPreset(index=`0x15`), **not** `MB_PlayLIM`.
  The shutdown we saw is a **preset** side-effect, not the PlayLIM opcode.
* Real LIM play uses opcode **`0x15`** with `buf[1] = limIndex`
  (`playLIM`).

### Wake / “I'm awake”

App `SendAwake()` calls `SendCommand(0x19, 0x1d)`, which builds:

```text
buf[0] = 0x19
buf[1..17] = 0x1d   (same byte repeated)
+ checksum
```

That matches pymecca’s `WAKE_COMMAND` / `wake_frame()`. Single-arg
`behaviour 0x1d` (index=`0x1d`, sub=`0`) is **not** the same payload.

## Other useful methods (for later probing)

From `BluetoothLE` public API (names only; see local IL dump for bodies):

`requestStatus`, `getName` / `setName`, `getTimeDate` / `setTimeDate`,
`setMapping`, `getServoPos` / `setServoPos` / `setServoMode`,
`setMotorValues`, `recordLIM`, `playLIM`, `getLIMInfo`, `deleteLIM`,
`changeLIMName`, `SendPIN`, `Subscribe` (notify on `FFF1`).

Robot-type constants: `drone`, `g15ks`, `g15`, `g16Drone`, `g16ks`, `g16`.

## How to reproduce the decompile

```bash
./third_party/apk/fetch-apk.sh
# jadx 1.5.x into third_party/apk/jadx-out (Java shell only)
# Extract Managed DLLs from the APK, then:
ikdasm assets/bin/Data/Managed/Assembly-CSharp.dll \
  > third_party/apk/csharp-il/Assembly-CSharp.il
```

Focus on class `BluetoothLE` and nested enum `MB_Commands`.

## Next steps

1. Add `0000fff2-…` (and service `fff0`) to pymecca write-char candidates;
   optionally subscribe to `fff1` for status/config replies.
2. Rename / alias CLI `behaviour` → `preset` in docs; keep `behaviour` as
   a synonym.
3. Implement thin wrappers for `playLIM`, `getServoPos`, `requestStatus`
   using the official opcodes.
4. HCI snoop the stock app to capture multi-byte presets / LIM traffic
   and any handshake beyond `SendPIN` / `SendAwake`.
