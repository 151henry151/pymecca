#!/usr/bin/env bash
# Fetch archived Meccanoid Android APK (not committed — ~97 MiB).
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$DIR/com.spinmaster.meccanoidrobot.apk"
EXPECTED_SHA256="${EXPECTED_SHA256:-6d460908d2808fe92a94cde13809bc2e9cf95ff2658a54cfd99dbacec34311ab}"
# Prefer Neil Fraser's archived last store build (same bytes as our research copy).
# Fallback: APKPure latest mirror (may change).
URL="${APK_URL:-https://neil.fraser.name/software/meccanoid/Android/Meccanoid_v4.02.48.apk}"
FALLBACK_URL="${APK_FALLBACK_URL:-https://d.apkpure.net/b/APK/com.spinmaster.meccanoidrobot?version=latest}"
if ! curl -fL --retry 3 -o "$OUT" "$URL"; then
  echo "Primary URL failed; trying fallback..." >&2
  curl -fL --retry 3 -o "$OUT" "$FALLBACK_URL"
fi
got="$(sha256sum "$OUT" | awk '{print $1}')"
if [[ "$got" != "$EXPECTED_SHA256" ]]; then
  echo "WARNING: SHA256 mismatch (mirror may have updated)." >&2
  echo "  expected: $EXPECTED_SHA256" >&2
  echo "  got:      $got" >&2
  echo "Update third_party/apk/SHA256SUMS if the new APK is intentional." >&2
fi
echo "Wrote $OUT ($got)"
