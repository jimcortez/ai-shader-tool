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
- **Python 3.8+** (for future Python bindings and development)
- **pyenv** (recommended for Python version management)

### Installing Dependencies

#### macOS
```bash
# Install system dependencies
brew install cmake glfw glew

# Install pyenv for Python version management (recommended)
brew install pyenv

# Set up pyenv (add to your shell profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Install Python 3.11 (recommended version)
pyenv install 3.11.7
pyenv global 3.11.7

# Verify installation
python --version
```

#### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt-get install cmake libglfw3-dev libglew-dev

# Install pyenv for Python version management (recommended)
curl https://pyenv.run | bash

# Set up pyenv (add to your shell profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Install Python 3.11 (recommended version)
pyenv install 3.11.7
pyenv global 3.11.7

# Verify installation
python --version
```

#### Windows
```bash
# Install CMake from https://cmake.org/download/
# Install GLFW and GLEW via vcpkg or build from source

# Install pyenv-win for Python version management (recommended)
# Download from: https://github.com/pyenv-win/pyenv-win

# Or use Chocolatey:
choco install pyenv-win

# Install Python 3.11 (recommended version)
pyenv install 3.11.7
pyenv global 3.11.7

# Verify installation
python --version
```

## Quick Start

### Python Environment Setup (Recommended)

Before building the project, we recommend setting up a Python environment using pyenv:

```bash
# Ensure you're using the recommended Python version
pyenv version

# If not using 3.11.7, set it:
pyenv local 3.11.7

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python environment
python --version
which python  # Should point to your pyenv-managed Python
```

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

#### 1. **"VVISF-GL submodule not found"**
**Error:** `external/VVISF-GL` directory is empty or missing

**Solution:**
```bash
# Initialize submodules
git submodule update --init --recursive

# Verify submodule status
git submodule status
```

**If still empty:**
```bash
# Remove and re-add the submodule
rm -rf external/VVISF-GL
git submodule add https://github.com/mrRay/VVISF-GL.git external/VVISF-GL
```

#### 2. **"GLFW3 not found"**
**Error:** Build fails with GLFW-related errors

**Solution:**
```bash
# macOS
brew install glfw

# Ubuntu/Debian
sudo apt-get install libglfw3-dev

# Windows
# Install via vcpkg or build from source
```

**Verify installation:**
```bash
# Check if GLFW is found
pkg-config --exists glfw3 && echo "GLFW found" || echo "GLFW not found"

# Check include paths
ls /opt/homebrew/include/GLFW/glfw3.h 2>/dev/null || ls /usr/local/include/GLFW/glfw3.h 2>/dev/null
```

#### 3. **"GLEW not found"**
**Error:** Build fails with GLEW-related errors

**Solution:**
```bash
# macOS
brew install glew

# Ubuntu/Debian
sudo apt-get install libglew-dev

# Windows
# Install via vcpkg or build from source
```

**Verify installation:**
```bash
# Check if GLEW is found
pkg-config --exists glew && echo "GLEW found" || echo "GLEW not found"

# Check include paths
ls /opt/homebrew/include/GL/glew.h 2>/dev/null || ls /usr/local/include/GL/glew.h 2>/dev/null
```

#### 4. **"Failed to apply GLFW patches"**
**Error:** Patch application fails during VVISF-GL build

**Solution:**
```bash
# Manual patch application
cd external/VVISF-GL
patch -p1 < ../../patches/vvisf-glfw-support.patch
```

**If patch still fails, apply changes manually:**

**Edit `external/VVISF-GL/VVGL/Makefile`:**
```makefile
# Find this line:
CPPFLAGS += -I./include/ -DVVGL_SDK_MAC

# Replace with:
CPPFLAGS += -I./include/ -DVVGL_SDK_GLFW
# Add GLFW and GLEW include paths
CPPFLAGS += -I/opt/homebrew/include

# Find this line:
LDFLAGS += -framework Foundation -framework ImageIO -framework OpenGL -framework IOSurface -framework CoreGraphics -framework CoreVideo

# Add after it:
# Add GLFW and GLEW libraries
LDFLAGS += -L/opt/homebrew/lib -lglfw -lGLEW
```

**Edit `external/VVISF-GL/VVISF/Makefile`:**
```makefile
# Same changes as above for VVGL/Makefile
```

#### 5. **"Build errors on macOS"**
**Error:** Various macOS-specific build errors

**Solution:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Verify installation
xcode-select -p
```

#### 6. **"Architecture mismatch errors"**
**Error:** Linking fails due to architecture mismatch

**Solution:**
```bash
# Check your architecture
uname -m

# For manual builds, specify architecture
ARCH=arm64 ./scripts/build_vvisf.sh  # For Apple Silicon
ARCH=x86_64 ./scripts/build_vvisf.sh # For Intel Macs
```

#### 7. **"CMake configuration failed"**
**Error:** CMake can't find dependencies or configure project

**Solution:**
```bash
# Clean build directory
rm -rf build
mkdir build
cd build

# Run CMake with verbose output
cmake -DCMAKE_VERBOSE_MAKEFILE=ON ..

# Check CMake cache
cat CMakeCache.txt | grep -E "(GLFW|GLEW|VVISF)"
```

#### 8. **"Submodule modified content"**
**Error:** Git shows modified content in submodules

**Solution:**
```bash
# Check submodule status
git submodule status

# Reset submodule to clean state
git submodule update --init --recursive --force

# Or commit the changes if they're intentional
cd external/VVISF-GL
git add .
git commit -m "Apply GLFW modifications"
```

#### 9. **"Python version issues"**
**Error:** Wrong Python version or pyenv not working

**Solution:**
```bash
# Check current Python version
python --version

# Check pyenv installation
pyenv --version

# List available Python versions
pyenv versions

# Set local Python version for this project
pyenv local 3.11.7

# Rehash pyenv (if needed)
pyenv rehash

# Verify Python path
which python
```

**If pyenv is not found:**
```bash
# macOS
brew install pyenv

# Ubuntu/Debian
curl https://pyenv.run | bash

# Windows
# Download from: https://github.com/pyenv-win/pyenv-win
```

### Debugging Steps

#### **Step-by-step debugging:**
1. **Check submodule status:**
   ```bash
   git submodule status
   ls -la external/VVISF-GL/
   ```

2. **Verify dependencies:**
   ```bash
   # Check GLFW
   pkg-config --modversion glfw3 2>/dev/null || echo "GLFW not found"
   
   # Check GLEW
   pkg-config --modversion glew 2>/dev/null || echo "GLEW not found"
   
   # Check CMake
   cmake --version
   
   # Check Python environment
   python --version
   which python
   pyenv version 2>/dev/null || echo "pyenv not found"
   ```

3. **Test patch application:**
   ```bash
   cd external/VVISF-GL
   patch --dry-run -p1 < ../../patches/vvisf-glfw-support.patch
   ```

4. **Check architecture compatibility:**
   ```bash
   uname -m
   file external/VVISF-GL/VVGL/bin/libVVGL.a 2>/dev/null || echo "Library not built yet"
   ```

5. **Run with verbose output:**
   ```bash
   # Verbose build script
   bash -x ./scripts/build_vvisf.sh
   
   # Verbose CMake
   cmake -DCMAKE_VERBOSE_MAKEFILE=ON ..
   ```

### Platform-Specific Notes

- **macOS**: Uses GLFW for cross-platform OpenGL context creation
- **Linux**: Uses GLFW with X11 backend
- **Windows**: Uses GLFW with Win32 backend

### Getting Help

If you're still experiencing issues:

1. **Check the logs:** Look for specific error messages in the build output
2. **Verify your environment:** Ensure all prerequisites are installed
3. **Try manual steps:** Follow the manual patch application instructions above
4. **Check architecture:** Ensure you're building for the correct architecture
5. **Clean rebuild:** Remove build artifacts and start fresh

**Common environment issues:**
- Missing Xcode Command Line Tools on macOS
- Outdated package managers (brew, apt)
- Incorrect PATH or library search paths
- Permission issues with system directories

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