#!/bin/bash

# TagFix Build Script
# This script builds the TagFix C++ application

set -e  # Exit on error

echo "=========================================="
echo "TagFix C++ Build Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for required tools
echo "Checking for required tools..."

check_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 found"
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        return 1
    fi
}

MISSING_TOOLS=0
check_tool cmake || MISSING_TOOLS=1
check_tool g++ || MISSING_TOOLS=1
check_tool pkg-config || MISSING_TOOLS=1

if [ $MISSING_TOOLS -eq 1 ]; then
    echo -e "${RED}Error: Missing required build tools${NC}"
    exit 1
fi

echo ""
echo "Checking for required libraries..."

check_lib() {
    if pkg-config --exists $1; then
        VERSION=$(pkg-config --modversion $1)
        echo -e "${GREEN}✓${NC} $1 found (version $VERSION)"
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        return 1
    fi
}

MISSING_LIBS=0
check_lib taglib || MISSING_LIBS=1
check_lib jsoncpp || MISSING_LIBS=1

# Qt5 check (different package name)
if pkg-config --exists Qt5Widgets Qt5Network; then
    VERSION=$(pkg-config --modversion Qt5Core)
    echo -e "${GREEN}✓${NC} Qt5 found (version $VERSION)"
else
    echo -e "${RED}✗${NC} Qt5 not found"
    MISSING_LIBS=1
fi

if [ $MISSING_LIBS -eq 1 ]; then
    echo ""
    echo -e "${RED}Error: Missing required libraries${NC}"
    echo ""
    echo "Install dependencies with:"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get install libtag1-dev libjsoncpp-dev qtbase5-dev"
    echo ""
    echo "Fedora/RHEL:"
    echo "  sudo dnf install taglib-devel jsoncpp-devel qt5-qtbase-devel"
    echo ""
    echo "macOS:"
    echo "  brew install taglib jsoncpp qt@5"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}All dependencies satisfied!${NC}"
echo ""

# Create build directory
BUILD_DIR="build"
if [ -d "$BUILD_DIR" ]; then
    echo -e "${YELLOW}Build directory exists, cleaning...${NC}"
    rm -rf "$BUILD_DIR"
fi

echo "Creating build directory..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo ""
echo "Configuring with CMake..."
cmake .. || {
    echo -e "${RED}CMake configuration failed${NC}"
    exit 1
}

echo ""
echo "Building..."
# Get number of cores in a portable way
NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
cmake --build . -j${NPROC} || {
    echo -e "${RED}Build failed${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}=========================================="
echo "Build successful!"
echo "==========================================${NC}"
echo ""
echo "Executable: $BUILD_DIR/TagFix"
echo ""
echo "To run the application:"
echo "  cd $BUILD_DIR && ./TagFix"
echo ""
echo "To install system-wide:"
echo "  cd $BUILD_DIR && sudo make install"
echo ""
