# Neil Fraser Meccanoid archive

Inventory of Meccanoid-related material on
[neil.fraser.name](https://neil.fraser.name/), compared with what pymecca
already mirrors. Surveyed 2026-08-09.

Primary index: https://neil.fraser.name/software/meccanoid/  
HTTP firmware CDN substitute: http://http.neil.fraser.name/mcnoid/  
(HTTP-only because the stock Robot Updater cannot fetch HTTPS.)

## Already in this repo

| Neil’s asset | Our copy / note |
|---|---|
| 2021-09-13 firmware-updater write-up | [`docs/reference/neil-fraser-2021-09-13.md`](reference/neil-fraser-2021-09-13.md); also linked from Revival README |
| Android app `Meccanoid_v4.02.48.apk` | Fetch helper + notes in [`third_party/apk/`](../third_party/apk/); 32-bit-only (`armeabi-v7a`/`x86`) |
| `Smart Module Protocols.pdf` | Same size as [`third_party/revival/Meccano_SmartModuleProtocols_2015.pdf`](../third_party/revival/Meccano_SmartModuleProtocols_2015.pdf) |
| `meccanoid-library.zip` | Same size as Revival’s official Arduino extract |
| Mentions of the updater in community lore | [`docs/UMPLESPLACE.md`](UMPLESPLACE.md) |

## Newly mirrored here (small / high value)

| Asset | Local path |
|---|---|
| `meccano123.json` (48 firmware catalog rows) | [`third_party/neil-fraser/meccano123.json`](../third_party/neil-fraser/meccano123.json) |
| `multi_language123.json` (updater UI strings) | [`third_party/neil-fraser/multi_language123.json`](../third_party/neil-fraser/multi_language123.json) |
| 2016-10-28 “Hackly” (kids build sessions) | [`docs/reference/neil-fraser-2016-10-28-hackly.md`](reference/neil-fraser-2016-10-28-hackly.md) |
| 2016-11-14 “Meccanoid Replication” (coworker build exercise) | [`docs/reference/neil-fraser-2016-11-14-replication.md`](reference/neil-fraser-2016-11-14-replication.md) |

`meccano123.json` is the Robot Updater’s catalog: model, language, `fw_version`,
dates, and original `cdn.meccano.com` ROM URLs. Neil hosts the actual binaries
under `http://http.neil.fraser.name/mcnoid/rom/…` (paths match the old CDN
layout). Useful for knowing which ROM names map to G15 vs G15KS vs 2.0 / XL /
Micronoid / M.A.X., and that US G15 tops out at **G15-2.8** /
**G15KS-2.8** (`20161219_us`, `MECCA_Small_SPI.bin` / `MECCA_Big_SPI.bin`).

## On Neil’s site but not mirrored in git (too large / optional)

Do **not** commit these unless we intentionally vendor them; keep remote
links or a local cache outside the repo.

### Firmware updater tools

* https://neil.fraser.name/software/meccanoid/RobotUpdaterSoftwareV1.28.5.zip (Windows installer, 9.4M)
* https://neil.fraser.name/software/meccanoid/MeccanoFirmwareUpdate.exe (patched exe, 5.0M)
* https://neil.fraser.name/software/meccanoid/RobotUpdaterSoftware_V1.23.pkg (macOS; Neil says broken on 10.13+)

### ROM images

Full tree: http://http.neil.fraser.name/mcnoid/rom/  
Language/date folders for G15/G15KS/2.0/XL, plus `max/` and `micronoid/`.  
Example US 2.8 G15/KS: `…/rom/20161219_us/` → `MECCA_Small_SPI.bin`,
`MECCA_Big_SPI.bin`, `ROMS.bin`, `ROMB.bin`.

### Construction manuals (Instructions/)

https://neil.fraser.name/software/meccanoid/Instructions/

| PDF | Notes vs our revival manuals |
|---|---|
| Meccanoid G15.pdf / G15KS.pdf | Stock humanoid manuals — **we do not have these** (revival has `15401b`/`15402b` only) |
| Meccanoid Dino G15.pdf / Dino G15KS.pdf | Dino builds — not in repo |
| Meccanoid 2.0.pdf / 2.0XL.pdf / Bug 2.0*.pdf | 2.0 family — not in repo |
| Meccabrain 2.0.pdf | Brain-focused — not in repo |
| Smart Module Protocols.pdf / meccanoid-library.zip | Already mirrored via Revival |

### Older Android APKs

https://neil.fraser.name/software/meccanoid/Android/

Neil hosts `v1.0` … `v2.4` plus `v4.02.45` / `.47` / `.48`. He notes older
builds fail (API / dead login). Still useful if we ever need to diff BLE
stacks across app versions. Only `v4.02.48` is wired into our fetch helper.

### Education PDFs (2016 kids workshops)

* https://neil.fraser.name/news/2016/Meccanoid%205%20team.pdf — 5-person build booklet (~9 MB)
* https://neil.fraser.name/news/2016/Meccanoid%20commands.pdf — post-build command card (~91 KB)

### Videos/

https://neil.fraser.name/software/meccanoid/Videos/ — firmware-update demo,
commercials, and long “Programming Meccanoid” training clips (hundreds of MB).
Low priority for BLE reverse engineering; useful for voice/UI vocabulary.

## Takeaways for pymecca

* **Firmware flasher still exists** via Neil’s patched Windows updater + HTTP
  ROM host — important if we ever need a known-good G15-2.8 reflash (umplesplace
  also stresses the updater).
* **Catalog JSON** encodes the product matrix (G15 small SPI vs G15KS big SPI,
  G16 “Full_Small/Big” for 2.0/XL, separate Micronoid/M.A.X. bins).
* **No BLE opcode map** on his site — education posts and manuals, not GATT.
* **Command card PDF** may list spoken / button commands worth cross-checking
  against our `0x19` behaviour map (not yet transcribed here).
* **Older APKs** are a possible next RE target if `v4.02.48` Unity code is a
  dead end for some presets.

## Suggested follow-ups (not done)

1. Download `Meccanoid commands.pdf` and note any voice phrases / menus we have
   not mapped under `behaviour 0x19`.
2. Optionally vendor G15 + G15KS construction PDFs next to revival manuals.
3. Keep ROMs / updater zips out of git; document a one-shot `fetch-firmware.sh`
   if we start flashing regularly.
4. Diff an older APK (`v2.4`) vs `v4.02.48` only if we need historical opcodes.
