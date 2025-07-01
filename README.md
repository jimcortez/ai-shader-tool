# AI Shader Tool

A Python project for rendering ISF (Interactive Shader Format) shaders using the VVISF-GL library, which provides C++ bindings for ISF shader rendering built on VVGL for OpenGL operations.

## Features

- Cross-platform ISF shader rendering using VVISF-GL
- GLFW-based OpenGL context creation for headless/offscreen rendering
- **Python bindings for VVISF** - Complete Python API for ISF shader rendering
- Support for macOS, Linux, and Windows
- Comprehensive ISF shader support (Source, Filter, Transition types)
- Real-time shader rendering with time-based animations
- Input attribute management and uniform control

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
   pytest ../tests
   ```

## Python API Documentation

The project provides comprehensive Python bindings for the VVISF library, allowing you to render ISF shaders directly from Python.

### Importing the Bindings

```python
import vvisf_bindings as vvisf

# Check platform and availability
print(f"Platform: {vvisf.get_platform_info()}")
print(f"VVISF Available: {vvisf.is_vvisf_available()}")
```

### Core Classes

#### ISFDoc - ISF Document Management

The `ISFDoc` class represents an ISF file and provides access to its properties and inputs.

```python
# Create ISFDoc from file
doc = vvisf.CreateISFDocRef("path/to/shader.fs")

# Access file properties
print(f"Name: {doc.name()}")
print(f"Description: {doc.description()}")
print(f"Type: {doc.type()}")  # ISFFileType.Source, Filter, or Transition

# Get all inputs
inputs = doc.inputs()
for input_attr in inputs:
    print(f"Input: {input_attr.name()} ({input_attr.type()})")

# Get specific input types
image_inputs = doc.image_inputs()
audio_inputs = doc.audio_inputs()

# Get shader source code
frag_source = doc.frag_shader_source()
vert_source = doc.vert_shader_source()
```

#### ISFScene - Shader Rendering

The `ISFScene` class handles the actual rendering of ISF shaders.

```python
# Create a scene
scene = vvisf.CreateISFSceneRef()

# Load an ISF file
scene.use_file("path/to/shader.fs")

# Set input values
scene.set_value_for_input_named(vvisf.ISFFloatVal(0.5), "intensity")
scene.set_value_for_input_named(vvisf.ISFColorVal(1.0, 0.0, 0.0, 1.0), "color")

# Render a frame
from vvisf_bindings import VVGL
size = VVGL.Size(1920, 1080)
buffer = scene.create_and_render_a_buffer(size)
```

#### ISFAttr - Input Attributes

The `ISFAttr` class represents individual input attributes in an ISF shader.

```python
# Get an input attribute
attr = scene.input_named("intensity")

# Access attribute properties
print(f"Name: {attr.name()}")
print(f"Type: {attr.type()}")
print(f"Description: {attr.description()}")

# Get current value
current_val = attr.current_val()
if current_val.is_float_val():
    print(f"Current value: {current_val.get_double_val()}")

# Set new value
attr.set_current_val(vvisf.ISFFloatVal(0.8))

# Constructing a new ISFAttr (advanced)
attr = vvisf.ISFAttr(
    "test_attr", "Test attribute", "Test", vvisf.ISFValType.Float,
    vvisf.ISFFloatVal(0.0), vvisf.ISFFloatVal(1.0), vvisf.ISFFloatVal(0.5), vvisf.ISFFloatVal(0.0),
    [], []  # labels and values are optional, usually empty lists
)
```

### Enum String Conversion

- Enum string conversion returns the value name, e.g. `str(vvisf.ISFValType.Float)` returns `'Float'`.

### Value Extraction

- Use `get_double_val()` for float values from ISFVal.
- Use `get_bool_val()`, `get_long_val()`, etc. for other types.

### Test Status

- **All tests pass and the API is stable as of the latest build.**

### Known Limitations

- Direct timestamp objects (e.g., VVGL::Timestamp) are not yet bound, but all core features are stable and tested.
- Enum string conversion returns the value name, not the full enum path.

### Value Types

The bindings support all ISF value types:

```python
# Boolean values
bool_val = vvisf.ISFBoolVal(True)

# Numeric values
long_val = vvisf.ISFLongVal(42)
float_val = vvisf.ISFFloatVal(3.14)

# 2D Points
point_val = vvisf.ISFPoint2DVal(100.0, 200.0)

# Colors (RGBA)
color_val = vvisf.ISFColorVal(1.0, 0.5, 0.0, 1.0)

# Events
event_val = vvisf.ISFEventVal(True)

# Null values
null_val = vvisf.ISFNullVal()
```

### Working with ISF Files

#### Scanning for ISF Files

```python
# Scan directory for ISF files
files = vvisf.scan_for_isf_files("/path/to/shaders")

# Filter by type
source_files = vvisf.scan_for_isf_files("/path/to/shaders", vvisf.ISFFileType.Source)
filter_files = vvisf.scan_for_isf_files("/path/to/shaders", vvisf.ISFFileType.Filter)

# Get default ISF files
default_files = vvisf.get_default_isf_files()

# Check if file is ISF
is_isf = vvisf.file_is_probably_isf("path/to/file.fs")
```

#### Complete Rendering Example

```python
import vvisf_bindings as vvisf
import time

# Create scene and load shader
scene = vvisf.CreateISFSceneRef()
scene.use_file("examples/shaders/example.fs")

# Set initial input values
scene.set_value_for_input_named(vvisf.ISFFloatVal(0.5), "speed")
scene.set_value_for_input_named(vvisf.ISFColorVal(1.0, 0.0, 0.0, 1.0), "baseColor")

# Render animation frames
for frame in range(60):
    # Update time-based inputs
    scene.set_value_for_input_named(vvisf.ISFFloatVal(frame * 0.1), "time")
    
    # Render frame
    size = vvisf.VVGL.Size(1920, 1080)
    buffer = scene.create_and_render_a_buffer(size)
    
    # Process buffer (save to file, display, etc.)
    # buffer contains the rendered image data
    
    time.sleep(1/30)  # 30 FPS
```

### Error Handling

The bindings include proper error handling:

```python
try:
    doc = vvisf.CreateISFDocRef("nonexistent.fs")
except vvisf.VVISFError as e:
    print(f"Error loading ISF file: {e}")
```

### Platform Support

The Python bindings work on all supported platforms:
- **macOS**: Full support with GLFW backend
- **Linux**: Full support with GLFW backend  
- **Windows**: Full support with GLFW backend

### Manual Setup

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
│   ├── vvisf_bindings.cpp # Python bindings for VVISF
│   └── isf_shader_renderer/
│       ├── __init__.py    # Python package
│       ├── cli.py         # Command-line interface
│       ├── config.py      # Configuration management
│       ├── renderer.py    # High-level renderer
│       └── utils.py       # Utility functions
├── tests/                 # Python test suite
├── examples/              # Example shaders and usage
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

### Testing

The project includes comprehensive tests for both C++ and Python components:

```bash
# Run C++ tests
cd build && ./vvisf_test

# Run Python tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/isf_shader_renderer --cov-report=html
```

### Testing Python Bindings

To test the new VVISF Python bindings:

```python
# Basic functionality test
import vvisf_bindings as vvisf

# Check availability
assert vvisf.is_vvisf_available()

# Test enum creation
assert vvisf.ISFValType.Float == vvisf.ISFValType.Float

# Test value creation
val = vvisf.ISFFloatVal(3.14)
assert val.is_float_val()
assert val.get_double_val() == 3.14
```

### Adding New Dependencies

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

#### 10. **"Python bindings not found"**
**Error:** `ModuleNotFoundError: No module named 'vvisf_bindings'`

**Solution:**
```bash
# Check if pybind11 is installed
brew list pybind11 2>/dev/null || echo "pybind11 not found"

# Install pybind11 if missing
brew install pybind11

# Rebuild the project
cd build
cmake ..
make vvisf_bindings

# Check if the module was built
ls -la src/isf_shader_renderer/vvisf_bindings*.so
```

#### 11. **"Python bindings import error"**
**Error:** Import succeeds but `vvisf.is_vvisf_available()` returns False

**Solution:**
```bash
# Check if VVISF libraries are built
ls -la external/VVISF-GL/VVGL/bin/libVVGL.a
ls -la external/VVISF-GL/VVISF/bin/libVVISF.a

# Rebuild VVISF if needed
./scripts/build_vvisf.sh

# Rebuild Python bindings
cd build && make vvisf_bindings
```

#### 12. **"OpenGL context creation failed"**
**Error:** Python bindings fail to create OpenGL context

**Solution:**
```bash
# Check GLFW installation
pkg-config --exists glfw3 && echo "GLFW found" || echo "GLFW not found"

# Check if running in headless environment
echo $DISPLAY  # Should be set on Linux
# On macOS, ensure you have proper graphics drivers
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