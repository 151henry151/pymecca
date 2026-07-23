# Archived Meccanoid Android APK

Package: `com.spinmaster.meccanoidrobot`  
Observed from this copy: **versionName `4.02`**, versionCode `48`  
(platform build 8.1.0 / API 27)

The APK itself is **not committed** (~97 MiB; GitHub warns above 50 MiB).
Fetch it locally:

```bash
./third_party/apk/fetch-apk.sh
```

Checksum of the copy used for research (2026-07-22):

```
6d460908d2808fe92a94cde13809bc2e9cf95ff2658a54cfd99dbacec34311ab  com.spinmaster.meccanoidrobot.apk
```

Also recorded in `SHA256SUMS`.

Permissions of interest (from `aapt dump badging`): Bluetooth,
Bluetooth admin, coarse location.

Findings are in [`docs/APK_ANALYSIS.md`](../../docs/APK_ANALYSIS.md).

Local decompile (gitignored):

```bash
# jadx → third_party/apk/jadx-out
# ikdasm Assembly-CSharp.dll → third_party/apk/csharp-il/
```
