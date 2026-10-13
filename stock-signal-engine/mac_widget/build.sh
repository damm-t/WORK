#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "🔨 Compiling QuantDesk macOS Menu Bar Widget with swiftc..."
swiftc -O -target arm64-apple-macosx26.0 main.swift -o QuantDeskWidget

echo "📦 Bundling into QuantDesk.app..."
APP_DIR="QuantDesk.app"
mkdir -p "$APP_DIR/Contents/MacOS"

cat << 'EOF' > "$APP_DIR/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>QuantDesk Widget</string>
    <key>CFBundleDisplayName</key>
    <string>QuantDesk Widget</string>
    <key>CFBundleIdentifier</key>
    <string>com.voonfamily.quantdesk.widget</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>QuantDeskWidget</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>
EOF

cp QuantDeskWidget "$APP_DIR/Contents/MacOS/QuantDeskWidget"
chmod +x "$APP_DIR/Contents/MacOS/QuantDeskWidget"

echo "✅ Build complete: $DIR/QuantDesk.app"
