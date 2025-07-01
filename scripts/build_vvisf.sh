#!/bin/bash
set -e

echo "Building VVISF-GL libraries with GLFW support..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VVISF_DIR="$PROJECT_ROOT/external/VVISF-GL"

# Check if VVISF-GL submodule exists
if [ ! -f "$VVISF_DIR/README.md" ]; then
    echo "Error: VVISF-GL submodule not found at $VVISF_DIR"
    echo "Run: git submodule update --init --recursive"
    exit 1
fi

# Detect architecture
if [[ $(uname -m) == "arm64" ]]; then
    ARCH="arm64"
    echo "Detected ARM64 architecture"
else
    ARCH="x86_64"
    echo "Detected x86_64 architecture"
fi

# Check if GLFW modifications are already applied
cd "$VVISF_DIR"
if ! grep -q "VVGL_SDK_GLFW" VVGL/Makefile; then
    echo "Error: GLFW modifications not applied to VVGL Makefile"
    echo "Please apply the GLFW support modifications manually"
    exit 1
fi

if ! grep -q "VVGL_SDK_GLFW" VVISF/Makefile; then
    echo "Error: GLFW modifications not applied to VVISF Makefile"
    echo "Please apply the GLFW support modifications manually"
    exit 1
fi

echo "GLFW modifications already applied"

# Build VVGL with GLFW support
echo "Building VVGL..."
cd VVGL
make clean
ARCH=$ARCH make
echo "✓ VVGL built successfully"

# Build VVISF with GLFW support
echo "Building VVISF..."
cd ../VVISF
make clean
ARCH=$ARCH make
echo "✓ VVISF built successfully"

echo "VVISF-GL libraries built successfully!"
echo "Libraries location:"
echo "  VVGL: $VVISF_DIR/VVGL/bin/libVVGL.a"
echo "  VVISF: $VVISF_DIR/VVISF/bin/libVVISF.a" 