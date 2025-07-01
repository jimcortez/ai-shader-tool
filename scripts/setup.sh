#!/bin/bash
set -e

echo "Setting up ai-shader-tool..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Initialize submodules
echo "Initializing git submodules..."
git submodule update --init --recursive

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v cmake &> /dev/null; then
    echo "Error: cmake not found. Please install cmake."
    exit 1
fi

if ! command -v make &> /dev/null; then
    echo "Error: make not found. Please install make."
    exit 1
fi

# Check for GLFW and GLEW
if ! pkg-config --exists glfw3; then
    echo "Warning: GLFW3 not found via pkg-config. Make sure it's installed."
fi

if ! pkg-config --exists glew; then
    echo "Warning: GLEW not found via pkg-config. Make sure it's installed."
fi

# Build VVISF-GL libraries
echo "Building VVISF-GL libraries..."
./scripts/build_vvisf.sh

# Build main project
echo "Building main project..."
mkdir -p build
cd build
cmake ..
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

echo "✓ Setup complete!"
echo ""
echo "To run tests:"
echo "  cd build && ./vvisf_test"
echo ""
echo "To build Python bindings (when implemented):"
echo "  cd build && make vvisf_bindings" 