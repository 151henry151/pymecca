# MEBLUSY opcode audit

Source mirrored under [`third_party/meblusy/`](../third_party/meblusy/).
Upstream: [antoniolosada/MEBLUSY](https://github.com/antoniolosada/MEBLUSY).

## Verdict

**No extra BLE opcodes** beyond the classic pymecca set.

`ComandosMeccanoid.py` is a near-copy of the original `iamsrp/pymecca`
`meccanoid.py` (Python 2 + pygatt + hardcoded GATT handle `0x001f`). The
Spanish `MecControlBLU.py` GUI only calls that wrapper.

## Opcodes present (same as pymecca)

| Opcode | Role |
|---:|---|
| `0x08` | Servo positions (8 channels + padding) |
| `0x0C` | Servo LED colours |
| `0x0D` | Drive wheels |
| `0x11` | Eye RGB |
| `0x19` | Behaviours / wake (`0x1d`×17 wake frame only) |
| `0x1C` | Chest lights |

MEBLUSY does **not** probe single-arg `behaviour` IDs; it only ships the
fixed “I'm awake” wake payload.

## Other content in MEBLUSY (not BLE)

- 3D print mounts (`Modelo3D/`)
- Inverse-kinematics / Geogebra notes under `DOCS/`
- PCB / mechanical photos

Useful as a Spanish-language front-end reference and confirmation that
another community fork never extended the wire protocol.
