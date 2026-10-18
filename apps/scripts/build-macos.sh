#!/usr/bin/env bash
# Build a Mac Catalyst version of the app that runs on this Mac, signed ad hoc
# ("Sign to Run Locally"), without an Apple developer account. See apps/README.md, "macOS".
#
# The committed iOS project (apps/ios) uses Swift Package Manager, whose prebuilt Capacitor
# binaries have no Mac Catalyst slice. This script therefore generates a throwaway
# CocoaPods-based copy of the iOS project in apps/build/macos-catalyst (gitignored), which
# compiles Capacitor from source, enables Catalyst there and builds it.
#
# Usage (from apps/):  PYTHON=../.venv/bin/python npm run macos   [CONFIGURATION=Debug]
# Result:              apps/build/macos/Guitar Positions.app
set -euo pipefail

APPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$APPS_DIR/build/macos-catalyst"
OUT="$APPS_DIR/build/macos"
CONFIGURATION="${CONFIGURATION:-Release}"
APP_NAME="Guitar Positions"

# CocoaPods fails with "invalid byte sequence" under a non-UTF-8 locale
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

cd "$APPS_DIR"
[ -d node_modules/@capacitor/ios ] || npm install
npm run bundle

rm -rf "$WORK"
mkdir -p "$WORK"
cp package.json capacitor.config.json "$WORK/"
cp -R www "$WORK/www"
ln -s "$APPS_DIR/node_modules" "$WORK/node_modules"

cd "$WORK"
npx cap add ios --packagemanager CocoaPods

# Enable Mac Catalyst for the app target (keeps the iOS bundle identifier)
PBXPROJ="ios/App/App.xcodeproj/project.pbxproj"
sed -i '' -E 's/^([[:space:]]*)PRODUCT_BUNDLE_IDENTIFIER = (.*);/\1PRODUCT_BUNDLE_IDENTIFIER = \2;\
\1SUPPORTS_MACCATALYST = YES;\
\1SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = NO;\
\1DERIVE_MACCATALYST_PRODUCT_BUNDLE_IDENTIFIER = NO;/' "$PBXPROJ"
grep -q 'SUPPORTS_MACCATALYST = YES' "$PBXPROJ" || { echo "Could not enable Mac Catalyst in $PBXPROJ" >&2; exit 1; }

xcodebuild \
  -workspace ios/App/App.xcworkspace -scheme App -configuration "$CONFIGURATION" \
  -destination 'generic/platform=macOS,variant=Mac Catalyst' \
  -derivedDataPath "$WORK/DerivedData" \
  CODE_SIGN_IDENTITY=- CODE_SIGN_STYLE=Manual DEVELOPMENT_TEAM= PROVISIONING_PROFILE_SPECIFIER= \
  ENABLE_HARDENED_RUNTIME=NO \
  build

rm -rf "$OUT/$APP_NAME.app"
mkdir -p "$OUT"
ditto "$WORK/DerivedData/Build/Products/$CONFIGURATION-maccatalyst/App.app" "$OUT/$APP_NAME.app"

# Re-sign inside-out so app and embedded frameworks carry one consistent ad hoc signature.
# With the hardened runtime on an ad hoc app, library validation makes dyld reject the
# frameworks ("different Team IDs"); the runtime is only needed for notarisation.
for framework in "$OUT/$APP_NAME.app"/Contents/Frameworks/*.framework; do
  [ -e "$framework" ] && codesign --force --sign - --timestamp=none "$framework"
done
codesign --force --sign - --timestamp=none "$OUT/$APP_NAME.app"
codesign --verify --deep --strict "$OUT/$APP_NAME.app"
if codesign -dv "$OUT/$APP_NAME.app" 2>&1 | grep -q 'flags=.*runtime'; then
  echo "Hardened runtime is still enabled on $OUT/$APP_NAME.app" >&2
  exit 1
fi
echo "Built $OUT/$APP_NAME.app"
