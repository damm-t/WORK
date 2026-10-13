#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Build if binary is missing
if [ ! -f "QuantDeskWidget" ]; then
    ./build.sh
fi

# Stop existing widget process if any
pkill -f 'QuantDeskWidget' 2>/dev/null || true
sleep 0.5

echo "🚀 Launching QuantDesk Menu Bar Widget..."
open -a "$DIR/QuantDesk.app" || nohup "$DIR/QuantDeskWidget" >/dev/null 2>&1 &

echo "✅ QuantDesk Widget is now running in your macOS Menu Bar (top right)!"
