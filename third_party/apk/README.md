# Archived Meccanoid Android APK

Package: `com.spinmaster.meccanoidrobot`  
Observed from this copy: **versionName `4.02`**, versionCode `48`  
(platform build 8.1.0 / API 27; `targetSdkVersion` 27; `minSdkVersion` 18)

Canonical public archive (Neil Fraser, 2021-09-13):

https://neil.fraser.name/software/meccanoid/Android/Meccanoid_v4.02.48.apk

The APK itself is **not committed** (~97 MiB; GitHub warns above 50 MiB).
Fetch it locally:

```bash
./third_party/apk/fetch-apk.sh
```

Checksum of the copy used for research (matches Neil’s archive):

```
6d460908d2808fe92a94cde13809bc2e9cf95ff2658a54cfd99dbacec34311ab  com.spinmaster.meccanoidrobot.apk
```

Also recorded in `SHA256SUMS`.

Native code ABIs in this APK: **`armeabi-v7a`** and **`x86` only** — no
`arm64-v8a`. Modern 64-bit-only phones (Galaxy S24/S25/S26 Ultra, recent
Pixels, etc.) reject install with `INSTALL_FAILED_NO_MATCHING_ABIS`. There is
no practical repack without 64-bit Unity/Mono libs. Use an older 32-bit-capable
phone, an x86 Android emulator, or control the robot with pymecca on a PC.

Permissions of interest (from `aapt dump badging`): Bluetooth,
Bluetooth admin, coarse location.

Findings are in [`docs/APK_ANALYSIS.md`](../../docs/APK_ANALYSIS.md).

Local decompile (gitignored):

```bash
# jadx → third_party/apk/jadx-out
# ikdasm Assembly-CSharp.dll → third_party/apk/csharp-il/
```
