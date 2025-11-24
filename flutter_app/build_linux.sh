#!/bin/bash
# TagFix Build Script for Linux
# This script builds a release version and creates an AppImage

set -e

echo "🔨 Building TagFix for Linux..."

# Navigate to flutter_app directory
cd "$(dirname "$0")"

# Build release
echo "📦 Building release binary..."
flutter build linux --release

# Check if build succeeded
if [ ! -d "build/linux/x64/release/bundle" ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo ""
echo "📍 Binary location: build/linux/x64/release/bundle/"
echo ""
echo "To run the app:"
echo "  cd build/linux/x64/release/bundle"
echo "  ./tagfix"
echo ""
echo "To create an AppImage, see DISTRIBUTION.md for instructions."
