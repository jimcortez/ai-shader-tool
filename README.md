# AI Shader Tool

A Python project for rendering ISF (Interactive Shader Format) shaders using the VVISF-GL library, which provides C++ bindings for ISF shader rendering built on VVGL for OpenGL operations.

## Features

- Cross-platform ISF shader rendering using VVISF-GL
- GLFW-based OpenGL context creation for headless/offscreen rendering
- Python bindings (planned)
- Support for macOS, Linux, and Windows

## Prerequisites

- **Git** (for submodule management)
- **CMake** (3.15 or later)
- **Make** or **Ninja**
- **C++ compiler** with C++11 support
- **GLFW3** and **GLEW** libraries

### Installing Dependencies

#### macOS
```bash
brew install cmake glfw glew
```

#### Ubuntu/Debian
```bash
sudo apt-get install cmake libglfw3-dev libglew-dev
```

#### Windows
- Install CMake from https://cmake.org/download/
- Install GLFW and GLEW via vcpkg or build from source

## Quick Start

### Fresh Clone Setup

1. **Clone the repository with submodules:**
   ```bash
   git clone --recursive https://github.com/your-username/ai-shader-tool.git
   cd ai-shader-tool
   ```

2. **Run the setup script:**
   ```bash
   ./scripts/setup.sh
   ```

   This script will:
   - Initialize all git submodules
   - Check prerequisites
   - Build VVISF-GL libraries with GLFW support
   - Build the main project

3. **Run tests:**
   ```bash
   cd build && ./vvisf_test
   ```

### Manual Setup

If you prefer manual setup or the setup script fails:

1. **Initialize submodules:**
   ```bash
   git submodule update --init --recursive
   ```

2. **Build VVISF-GL libraries:**
   ```bash
   ./scripts/build_vvisf.sh
   ```

3. **Build the main project:**
   ```bash
   mkdir -p build && cd build
   cmake ..
   make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
   ```

## Project Structure

```
ai-shader-tool/
├── external/
│   └── VVISF-GL/          # Git submodule - VVISF-GL library
│       ├── VVGL/          # VVGL graphics library
│       └── VVISF/         # VVISF ISF rendering library
├── scripts/
│   ├── setup.sh           # Complete setup script
│   └── build_vvisf.sh     # VVISF-GL build script
├── src/
│   ├── vvisf_test.cpp     # C++ test executable
│   └── vvisf_bindings.cpp # Python bindings (planned)
├── build/                 # Build output directory
└── CMakeLists.txt         # Main CMake configuration
```

## Development

### Updating VVISF-GL

To update to a newer version of VVISF-GL:

```bash
cd external/VVISF-GL
git pull origin main
cd ../..
./scripts/build_vvisf.sh
```

### Adding New Dependencies

When adding new external dependencies:

1. Add them as git submodules in `external/`
2. Update `.gitignore` to exclude build artifacts but allow submodule content
3. Create build scripts in `scripts/`
4. Update `CMakeLists.txt` to find and link the new dependencies

## Troubleshooting

### Common Issues

1. **"VVISF-GL submodule not found"**
   - Run: `git submodule update --init --recursive`

2. **"GLFW3 not found"**
   - Install GLFW: `brew install glfw` (macOS) or `sudo apt-get install libglfw3-dev` (Ubuntu)

3. **"GLEW not found"**
   - Install GLEW: `brew install glew` (macOS) or `sudo apt-get install libglew-dev` (Ubuntu)

4. **Build errors on macOS**
   - Ensure you have Xcode Command Line Tools: `xcode-select --install`

5. **Architecture mismatch errors**
   - The build script automatically detects architecture (ARM64/x86_64)
   - For manual builds, set `ARCH=arm64` or `ARCH=x86_64` as needed

### Platform-Specific Notes

- **macOS**: Uses GLFW for cross-platform OpenGL context creation
- **Linux**: Uses GLFW with X11 backend
- **Windows**: Uses GLFW with Win32 backend

## Current Status

### ✅ Completed (Step 1)
- **GLFW Integration**: Successfully integrated GLFW for cross-platform OpenGL context creation
- **VVISF-GL Build System**: Created automated build scripts for VVISF-GL with GLFW support
- **Git Submodules**: Set up proper dependency management using git submodules
- **Cross-Platform Support**: Working on macOS with ARM64 architecture
- **OpenGL Context Creation**: Successfully creating hidden GLFW windows for offscreen rendering
- **VVISF Scene Creation**: Basic VVISF scene instantiation working

### 🔄 In Progress
- **Python Bindings**: Planned using pybind11
- **ISF Shader Loading**: Integration with actual ISF shader files
- **Rendering Pipeline**: Complete rendering workflow

### 📋 Planned
- **CLI Interface**: Command-line tool for shader rendering
- **Configuration System**: YAML-based configuration
- **Batch Processing**: Multiple shader rendering
- **Output Formats**: PNG, JPEG, and other image formats

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here] 