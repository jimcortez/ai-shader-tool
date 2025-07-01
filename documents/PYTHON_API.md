# VVISF Python API Documentation

> For build, troubleshooting, and AI/developer notes, see [ai-coding-documentation.md](ai-coding-documentation.md).

This document provides comprehensive documentation for the VVISF Python bindings and the high-level ShaderRenderer API, which allow you to render ISF (Interactive Shader Format) shaders directly from Python.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [High-Level API - ShaderRenderer](#high-level-api---shaderrenderer)
3. [Configuration System](#configuration-system)
4. [Low-Level API - VVISF Bindings](#low-level-api---vvisf-bindings)
5. [Core Classes](#core-classes)
6. [Value Types](#value-types)
7. [Working with ISF Files](#working-with-isf-files)
8. [Rendering Examples](#rendering-examples)
9. [Error Handling](#error-handling)
10. [Performance Considerations](#performance-considerations)
11. [Platform Support](#platform-support)
12. [Platform Abstraction and Fallbacks](#platform-abstraction-and-fallbacks)
13. [Performance Features](#performance-features)

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- VVISF-GL library (built with GLFW support)
- pybind11 (for building the bindings)

### Building the Bindings

The Python bindings are built automatically when you run the setup script:

```bash
./scripts/setup.sh
```

Or manually:

```bash
# Install pybind11
brew install pybind11  # macOS
# or
sudo apt-get install pybind11-dev  # Ubuntu/Debian

# Build the bindings
cd build
cmake ..
make vvisf_bindings
```

### Installing the Package

```bash
# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Importing the Modules

```python
# High-level API
from isf_shader_renderer.renderer import ShaderRenderer
from isf_shader_renderer.config import ShaderRendererConfig, Defaults, ShaderConfig

# Low-level API
import isf_shader_renderer.vvisf_bindings as vvisf

# Check if VVISF is available
if not vvisf.is_vvisf_available():
    print("Warning: VVISF is not available, using placeholder renderer")

# Get platform information
print(f"Platform: {vvisf.get_platform_info()}")
```

## High-Level API - ShaderRenderer

The `ShaderRenderer` class provides a simple, high-level interface for rendering ISF shaders to images. It handles OpenGL context management, shader loading, input setting, and image output automatically.

### Basic Usage

```python
from isf_shader_renderer.renderer import ShaderRenderer
from isf_shader_renderer.config import ShaderRendererConfig, Defaults
from pathlib import Path

# Create configuration
config = ShaderRendererConfig()
config.defaults = Defaults(width=1920, height=1080, quality=95)

# Create renderer
renderer = ShaderRenderer(config)

# Render a simple shader
shader_content = """/*{
    "DESCRIPTION": "Test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}"""

# Render frame at time 0.0
output_path = Path("output/test_frame.png")
renderer.render_frame(shader_content, 0.0, output_path)
```

### Rendering with Custom Inputs

```python
from isf_shader_renderer.config import ShaderConfig

# Create shader configuration with custom inputs
shader_config = ShaderConfig(
    input="eye_shader.fs",
    output="output/eye_%04d.png",
    times=[0.0, 1.0, 2.0],
    width=1280,
    height=720,
    inputs={
        "irisHue": 0.6,
        "pupilSize": 0.15,
        "eyeMovementSpeed": 1.2,
        "reflectionIntensity": 0.8
    }
)

# Render with custom configuration
renderer.render_frame(
    shader_content,
    1.5,
    Path("output/eye_with_inputs.png"),
    shader_config
)
```

### Shader Validation and Information

```python
# Validate shader
is_valid = renderer.validate_shader(shader_content)
print(f"Shader is valid: {is_valid}")

# Get detailed shader information
info = renderer.get_shader_info(shader_content)
print(f"Shader name: {info['name']}")
print(f"Description: {info['description']}")
print(f"Inputs: {len(info['inputs'])}")
for input_info in info['inputs']:
    print(f"  - {input_info['name']}: {input_info['type']}")
    print(f"    Description: {input_info['description']}")
    print(f"    Label: {input_info['label']}")
```

### Batch Rendering

```python
# Render multiple frames
times = [0.0, 0.5, 1.0, 1.5, 2.0]
for i, time_code in enumerate(times):
    output_path = Path(f"output/frame_{i:04d}.png")
    renderer.render_frame(shader_content, time_code, output_path)
    print(f"Rendered frame {i+1}/{len(times)}")

# Clean up resources
renderer.cleanup()
```

### Complex Shader Example

```python
# Render a complex spherical eye shader
complex_shader = """/*{
    "CATEGORIES": [],
    "CREDIT": "Jim Cortez - Commune Project",
    "DESCRIPTION": "Advanced spherical human eyeball with realistic anatomy",
    "INPUTS": [
        {"NAME": "irisHue", "TYPE": "float", "DEFAULT": 0.6, "MIN": 0.0, "MAX": 1.0},
        {"NAME": "pupilSize", "TYPE": "float", "DEFAULT": 0.12, "MIN": 0.05, "MAX": 0.3},
        {"NAME": "eyeMovementSpeed", "TYPE": "float", "DEFAULT": 0.8, "MIN": 0.0, "MAX": 3.0}
    ],
    "ISFVSN": "2"
}*/
// ... shader code ...
void main() {
    // Complex eye rendering logic
    gl_FragColor = vec4(col, 1.0);
}"""

# Render with custom parameters
shader_config = ShaderConfig(
    input="eye.fs",
    output="output/eye.png",
    times=[0.0],
    width=1920,
    height=1080,
    inputs={
        "irisHue": 0.8,        # Blue iris
        "pupilSize": 0.15,     # Larger pupil
        "eyeMovementSpeed": 1.2 # Faster movement
    }
)

renderer.render_frame(complex_shader, 0.0, Path("output/eye.png"), shader_config)
```

### Error Handling and Fallbacks

The ShaderRenderer includes robust error handling and fallbacks:

```python
# If VVISF is not available, the renderer falls back to placeholder rendering
if not vvisf.is_vvisf_available():
    print("Warning: Using placeholder renderer")
    # The renderer will still work, but with placeholder images

# The renderer handles shader errors gracefully
try:
    renderer.render_frame(invalid_shader, 0.0, output_path)
except Exception as e:
    print(f"Rendering failed: {e}")
    # The renderer will create a fallback image
    # NEW: Access the error log for details
    doc = vvisf.CreateISFDocRefWith(invalid_shader)
    print(f"Shader error log: {doc.error_log}")
```

## Configuration System

The project includes a YAML-based configuration system for batch rendering.

### Configuration File Example

```yaml
defaults:
  width: 1920
  height: 1080
  quality: 95
  output_format: png
  max_texture_size: 4096  # Maximum allowed width/height for rendered images (default: 4096)

shaders:
  - input: "shaders/example.fs"
    output: "output/example_%04d.png"
    times: [0.0, 0.5, 1.0, 1.5, 2.0]
    width: 1280
    height: 720
    inputs:
      color: [1.0, 0.0, 0.0, 1.0]
      speed: 2.0

  - input: "shaders/eye.fs"
    output: "output/eye_%04d.png"
    times: [0.0, 1.0, 2.0, 3.0]
    width: 1920
    height: 1080
    inputs:
      irisHue: 0.6
      pupilSize: 0.12
      eyeMovementSpeed: 0.8
```

#### max_texture_size (Defaults)
- **Type:** integer (default: 4096)
- **Description:** Maximum allowed width or height for any rendered image. If a render request exceeds this size, the renderer will clamp the output to this limit and log a warning. This helps prevent excessive memory usage or accidental oversized renders.

### Loading and Using Configuration

```python
from isf_shader_renderer.config import load_config, save_config, create_default_config

# Load configuration from file
config = load_config(Path("config.yaml"))

# Create renderer with configuration
renderer = ShaderRenderer(config)

# Render all shaders in configuration
for shader_config in config.shaders:
    # Load shader content from file
    with open(shader_config.input, 'r') as f:
        shader_content = f.read()

    # Render all time frames
    for time_code in shader_config.times:
        output_path = Path(shader_config.output.replace("%04d", f"{int(time_code*100):04d}"))
        renderer.render_frame(shader_content, time_code, output_path, shader_config)

# Save configuration
save_config(config, Path("config_updated.yaml"))

# Create default configuration
create_default_config(Path("config_default.yaml"))
```

### Configuration Classes

```python
from isf_shader_renderer.config import ShaderRendererConfig, Defaults, ShaderConfig

# Create configuration programmatically
config = ShaderRendererConfig()

# Set defaults
config.defaults = Defaults(
    width=1920,
    height=1080,
    quality=95,
    output_format="png"
)

# Add shader configurations
shader_config = ShaderConfig(
    input="shaders/test.fs",
    output="output/test_%04d.png",
    times=[0.0, 1.0, 2.0],
    width=1280,
    height=720,
    quality=90,
    inputs={
        "intensity": 0.8,
        "color": [1.0, 0.0, 0.0, 1.0]
    }
)
config.shaders.append(shader_config)
```

## Low-Level API - VVISF Bindings

The project also provides direct access to the VVISF library through Python bindings.

### Importing the Bindings

```python
import isf_shader_renderer.vvisf_bindings as vvisf

# Check platform and availability
print(f"Platform: {vvisf.get_platform_info()}")
print(f"VVISF Available: {vvisf.is_vvisf_available()}")
```

## Core Classes

### ISFDoc

The `ISFDoc` class represents an ISF file and provides access to its metadata, inputs, and source code.

#### Creation

```python
# Create from file
doc = vvisf.CreateISFDocRef("path/to/shader.fs")

# Create from shader strings
frag_source = """
/*{
    "DESCRIPTION": "My shader",
    "INPUTS": [
        {
            "NAME": "intensity",
            "TYPE": "float",
            "DEFAULT": 0.5
        }
    ]
}*/

void main() {
    gl_FragColor = vec4(intensity, 0.0, 0.0, 1.0);
}
"""
doc = vvisf.CreateISFDocRefWith(frag_source, "/path/to/imports")
```

#### Properties

```python
# File properties
print(f"Name: {doc.name()}")
print(f"Description: {doc.description()}")
print(f"Credit: {doc.credit()}")
print(f"Version: {doc.vsn()}")
print(f"Type: {doc.type()}")  # ISFFileType enum
print(f"Categories: {doc.categories()}")

# NEW: Shader compilation error log
# If shader compilation fails, you can access the error log:
if not doc.is_valid():
    print(f"Shader error log: {doc.error_log}")
# Or after attempting to load/compile a shader:
print(f"Last error log: {doc.error_log}")

# File type constants
print(vvisf.ISFFileType.Source)      # 1
print(vvisf.ISFFileType.Filter)      # 2
print(vvisf.ISFFileType.Transition)  # 4
print(vvisf.ISFFileType.All)         # 7
```

#### Inputs

```python
# Get all inputs
inputs = doc.inputs()
for input_attr in inputs:
    print(f"Input: {input_attr.name()} ({input_attr.type()})")

# Get specific input types
image_inputs = doc.image_inputs()
audio_inputs = doc.audio_inputs()
audio_fft_inputs = doc.audio_inputs()  # Same as audio_inputs

# Get inputs by type
float_inputs = doc.inputs_of_type(vvisf.ISFValType.Float)
color_inputs = doc.inputs_of_type(vvisf.ISFValType.Color)

# Get specific input
intensity_input = doc.input("intensity")
```

#### Source Code

```python
# Get shader source code
frag_source = doc.frag_shader_source()
vert_source = doc.vert_shader_source()

# Get JSON metadata
json_source = doc.json_source_string()  # With comments
json_clean = doc.json_string()          # Clean JSON

# Generate shader source for specific OpenGL version
frag_out = ""
vert_out = ""
gl_version = vvisf.VVGL.GLVersion.GL2
success = doc.generate_shader_source(frag_out, vert_out, gl_version)
```

### ISFScene

The `ISFScene` class handles the actual rendering of ISF shaders.

#### Creation and Setup

```python
# Create scene with default OpenGL context
scene = vvisf.CreateISFSceneRef()

# Create scene with custom OpenGL context (advanced)
# context = vvisf.VVGL.CreateNewGLContextRef()
# scene = vvisf.CreateISFSceneRefUsing(context)

# Load ISF file
scene.use_file("path/to/shader.fs")

# Or load from ISFDoc
doc = vvisf.CreateISFDocRef("path/to/shader.fs")
scene.use_doc(doc)

# Get the loaded document
current_doc = scene.doc()
```

#### Rendering

```python
# Basic rendering
size = vvisf.VVGL.Size(1920, 1080)
buffer = scene.create_and_render_a_buffer(size)

# Render with custom time
import time
current_time = time.time()
buffer = scene.create_and_render_a_buffer(size, current_time)

# Render to existing buffer (advanced)
# target_buffer = vvisf.VVGL.CreateBufferRef(size)
# scene.render_to_buffer(target_buffer, size)
```

#### Input Management

```python
# Set values by name
scene.set_value_for_input_named(vvisf.ISFFloatVal(0.5), "intensity")
scene.set_value_for_input_named(vvisf.ISFColorVal(1.0, 0.0, 0.0, 1.0), "color")
scene.set_value_for_input_named(vvisf.ISFPoint2DVal(100.0, 200.0), "position")

# Set image inputs
# image_buffer = vvisf.VVGL.CreateBufferRef(size)
# scene.set_buffer_for_input_named(image_buffer, "inputImage")

# Set filter input (for filter-type shaders)
# scene.set_filter_input_buffer(image_buffer)

# Get current values
intensity_val = scene.value_for_input_named("intensity")
print(f"Current intensity: {intensity_val.get_float_val()}")
```

#### Time and Animation

```python
# Set base time for animations
import time
scene.set_base_time(time.time())

# Get current timestamp
timestamp = scene.get_timestamp()
print(f"Current time: {timestamp}")

# Set render size
scene.set_size(vvisf.VVGL.Size(1920, 1080))
current_size = scene.size()
render_size = scene.render_size()
```

#### Input Attributes

```python
# Get input attributes
inputs = scene.inputs()
for input_attr in inputs:
    print(f"Input: {input_attr.name()}")

# Get specific input
intensity_attr = scene.input_named("intensity")

# Get inputs by type
float_inputs = scene.inputs_of_type(vvisf.ISFValType.Float)
image_inputs = scene.image_inputs()
audio_inputs = scene.audio_inputs()
```

### ISFAttr

The `ISFAttr` class represents individual input attributes in an ISF shader.

#### Properties

```python
# Basic properties
print(f"Name: {attr.name()}")
print(f"Description: {attr.description()}")
print(f"Label: {attr.label()}")
print(f"Type: {attr.type()}")

# Value properties
current_val = attr.current_val()
min_val = attr.min_val()
max_val = attr.max_val()
default_val = attr.default_val()
identity_val = attr.identity_val()

# Special properties
is_filter_input = attr.is_filter_input_image()
is_trans_start = attr.is_trans_start_image()
is_trans_end = attr.is_trans_end_image()
is_trans_progress = attr.is_trans_progress_float()
```

#### Value Management

```python
# Get current value
current_val = attr.current_val()
if current_val.is_float_val():
    print(f"Float value: {current_val.get_float_val()}")
elif current_val.is_color_val():
    r = current_val.get_color_val_by_channel(0)
    g = current_val.get_color_val_by_channel(1)
    b = current_val.get_color_val_by_channel(2)
    a = current_val.get_color_val_by_channel(3)
    print(f"Color: ({r}, {g}, {b}, {a})")

# Set new value
attr.set_current_val(vvisf.ISFFloatVal(0.8))

# For image inputs
if attr.should_have_image_buffer():
    # image_buffer = vvisf.VVGL.CreateBufferRef(size)
    # attr.set_current_image_buffer(image_buffer)
    current_image = attr.get_current_image_buffer()
```

#### Long/Enum Values

```python
# For long-type inputs with labels
if attr.type() == vvisf.ISFValType.Long:
    labels = attr.label_array()
    values = attr.val_array()
    for label, value in zip(labels, values):
        print(f"{label}: {value}")
```

#### Construction

The recommended way to construct an ISFAttr in Python is:

```python
attr = vvisf.ISFAttr(
    "test_attr", "Test attribute", "Test", vvisf.ISFValType.Float,
    vvisf.ISFFloatVal(0.0), vvisf.ISFFloatVal(1.0), vvisf.ISFFloatVal(0.5), vvisf.ISFFloatVal(0.0),
    [], []  # labels and values are optional, usually empty lists
)
```

### ISFVal Methods

- Use `get_double_val()` for float values.
- Use `get_bool_val()`, `get_long_val()`, etc. for other types.

### Enum String Conversion

- `str(vvisf.ISFValType.Float)` returns `'Float'`.

### Known Limitations

- Direct timestamp objects (e.g., VVGL::Timestamp) are not yet bound, but all core features are stable and tested.
- Enum string conversion returns the value name, not the full enum path.

### Test Status

- **All tests pass and the API is stable as of the latest build.**

## Value Types

The bindings support all ISF value types through the `ISFVal` class and creation functions.

### Creation Functions

```python
# Null value
null_val = vvisf.ISFNullVal()

# Boolean
bool_val = vvisf.ISFBoolVal(True)

# Numeric
long_val = vvisf.ISFLongVal(42)
float_val = vvisf.ISFFloatVal(3.14)

# 2D Point
point_val = vvisf.ISFPoint2DVal(100.0, 200.0)

# Color (RGBA)
color_val = vvisf.ISFColorVal(1.0, 0.5, 0.0, 1.0)

# Event
event_val = vvisf.ISFEventVal(True)

# Image (advanced)
# image_buffer = vvisf.VVGL.CreateBufferRef(size)
# image_val = vvisf.ISFImageVal(image_buffer)
```

### ISFVal Methods

```python
# Type checking
val = vvisf.ISFFloatVal(3.14)
print(val.is_float_val())      # True
print(val.is_color_val())      # False
print(val.is_null_val())       # False

# Value extraction
float_val = val.get_float_val()
double_val = val.get_double_val()
bool_val = val.get_bool_val()
long_val = val.get_long_val()

# Point values
point_val = vvisf.ISFPoint2DVal(100.0, 200.0)
x = point_val.get_point_val_by_index(0)  # 100.0
y = point_val.get_point_val_by_index(1)  # 200.0

# Color values
color_val = vvisf.ISFColorVal(1.0, 0.5, 0.0, 1.0)
r = color_val.get_color_val_by_channel(0)  # 1.0
g = color_val.get_color_val_by_channel(1)  # 0.5
b = color_val.get_color_val_by_channel(2)  # 0.0
a = color_val.get_color_val_by_channel(3)  # 1.0

# String representation
print(val.get_type_string())   # "float"
print(val.get_val_string())    # "3.14"
```

### Value Type Constants

```python
# Available value types
print(vvisf.ISFValType.None)       # 0
print(vvisf.ISFValType.Event)      # 1
print(vvisf.ISFValType.Bool)       # 2
print(vvisf.ISFValType.Long)       # 3
print(vvisf.ISFValType.Float)      # 4
print(vvisf.ISFValType.Point2D)    # 5
print(vvisf.ISFValType.Color)      # 6
print(vvisf.ISFValType.Cube)       # 7
print(vvisf.ISFValType.Image)      # 8
print(vvisf.ISFValType.Audio)      # 9
print(vvisf.ISFValType.AudioFFT)   # 10

# Check if type uses image
print(vvisf.ISFValType.Image.uses_image())      # True
print(vvisf.ISFValType.Float.uses_image())      # False
```

## Working with ISF Files

### File Discovery

```python
# Scan directory for ISF files
files = vvisf.scan_for_isf_files("/path/to/shaders")
print(f"Found {len(files)} ISF files")

# Filter by type
source_files = vvisf.scan_for_isf_files("/path/to/shaders", vvisf.ISFFileType.Source)
filter_files = vvisf.scan_for_isf_files("/path/to/shaders", vvisf.ISFFileType.Filter)
transition_files = vvisf.scan_for_isf_files("/path/to/shaders", vvisf.ISFFileType.Transition)

# Recursive scanning
all_files = vvisf.scan_for_isf_files("/path/to/shaders", recursive=True)

# Get default ISF files
default_files = vvisf.get_default_isf_files()

# Check if file is ISF
is_isf = vvisf.file_is_probably_isf("path/to/file.fs")
```

### File Analysis

```python
def analyze_isf_file(file_path):
    """Analyze an ISF file and print its properties."""
    try:
        doc = vvisf.CreateISFDocRef(file_path)

        print(f"File: {file_path}")
        print(f"Name: {doc.name()}")
        print(f"Description: {doc.description()}")
        print(f"Type: {doc.type()}")
        print(f"Categories: {doc.categories()}")

        print("\nInputs:")
        for input_attr in doc.inputs():
            print(f"  - {input_attr.name()}: {input_attr.type()}")
            if input_attr.description():
                print(f"    Description: {input_attr.description()}")

        print(f"\nRender passes: {doc.render_passes()}")

    except vvisf.VVISFError as e:
        print(f"Error analyzing {file_path}: {e}")

# Usage
analyze_isf_file("path/to/shader.fs")
```

## Rendering Examples

### Basic Animation

```python
import vvisf_bindings as vvisf
import time

# Create scene and load shader
scene = vvisf.CreateISFSceneRef()
scene.use_file("examples/shaders/animation.fs")

# Set initial values
scene.set_value_for_input_named(vvisf.ISFFloatVal(0.5), "speed")
scene.set_value_for_input_named(vvisf.ISFColorVal(1.0, 0.0, 0.0, 1.0), "baseColor")

# Animation loop
start_time = time.time()
for frame in range(60):
    # Calculate current time
    current_time = time.time() - start_time

    # Update time-based inputs
    scene.set_value_for_input_named(vvisf.ISFFloatVal(current_time), "time")

    # Render frame
    size = vvisf.VVGL.Size(1920, 1080)
    buffer = scene.create_and_render_a_buffer(size)

    # Process buffer (save to file, display, etc.)
    print(f"Rendered frame {frame}")

    time.sleep(1/30)  # 30 FPS
```

### Interactive Shader Control

```python
import vvisf_bindings as vvisf

def create_interactive_shader(shader_path):
    """Create an interactive shader with real-time parameter control."""
    scene = vvisf.CreateISFSceneRef()
    scene.use_file(shader_path)

    # Get all float inputs for interactive control
    float_inputs = scene.inputs_of_type(vvisf.ISFValType.Float)

    print("Available float inputs:")
    for i, input_attr in enumerate(float_inputs):
        print(f"{i}: {input_attr.name()} (default: {input_attr.default_val().get_float_val()})")

    return scene, float_inputs

def render_with_parameters(scene, parameters):
    """Render a frame with the given parameters."""
    size = vvisf.VVGL.Size(1920, 1080)

    # Set all parameters
    for input_attr, value in parameters.items():
        scene.set_value_for_input_named(vvisf.ISFFloatVal(value), input_attr.name())

    # Render
    return scene.create_and_render_a_buffer(size)

# Usage
scene, inputs = create_interactive_shader("path/to/shader.fs")

# Set some parameters
params = {
    inputs[0]: 0.7,  # First float input
    inputs[1]: 0.3,  # Second float input
}

buffer = render_with_parameters(scene, params)
```

### Batch Rendering

```python
import vvisf_bindings as vvisf
import os

def batch_render_shaders(shader_dir, output_dir, size=(1920, 1080)):
    """Render all ISF files in a directory."""
    # Find all ISF files
    isf_files = vvisf.scan_for_isf_files(shader_dir)

    for shader_file in isf_files:
        try:
            # Create scene
            scene = vvisf.CreateISFSceneRef()
            scene.use_file(shader_file)

            # Render frame
            render_size = vvisf.VVGL.Size(size[0], size[1])
            buffer = scene.create_and_render_a_buffer(render_size)

            # Save buffer (implementation depends on your needs)
            output_file = os.path.join(output_dir, f"{os.path.basename(shader_file)}.png")
            # save_buffer_to_file(buffer, output_file)

            print(f"Rendered: {shader_file}")

        except vvisf.VVISFError as e:
            print(f"Error rendering {shader_file}: {e}")

# Usage
batch_render_shaders("shaders/", "output/")
```

## Error Handling

### Exception Types

```python
import vvisf_bindings as vvisf

try:
    # This might fail
    doc = vvisf.CreateISFDocRef("nonexistent.fs")
except vvisf.VVISFError as e:
    print(f"VVISF error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Common Error Scenarios

```python
def safe_render_shader(shader_path, parameters=None, size=(1920, 1080)):
    """Safely render a shader with comprehensive error handling."""
    try:
        # Validate inputs
        if not os.path.exists(shader_path):
            raise FileNotFoundError(f"Shader file not found: {shader_path}")

        # Check if file is ISF
        if not vvisf.file_is_probably_isf(shader_path):
            raise ValueError(f"File does not appear to be an ISF: {shader_path}")

        # Create scene
        scene = vvisf.CreateISFSceneRef()
        scene.use_file(shader_path)

        # Set parameters
        if parameters:
            for name, value in parameters.items():
                try:
                    scene.set_value_for_input_named(value, name)
                except Exception as e:
                    print(f"Warning: Failed to set parameter {name}: {e}")

        # Render
        render_size = vvisf.VVGL.Size(size[0], size[1])
        buffer = scene.create_and_render_a_buffer(render_size)

        return buffer

    except vvisf.VVISFError as e:
        print(f"VVISF error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Performance Considerations

### Memory Management

```python
# The bindings use shared_ptr for automatic memory management
# No manual cleanup is required, but you can help the garbage collector

def render_multiple_frames(scene, num_frames):
    """Render multiple frames efficiently."""
    buffers = []

    for i in range(num_frames):
        # Render frame
        buffer = scene.create_and_render_a_buffer(vvisf.VVGL.Size(1920, 1080))
        buffers.append(buffer)

        # Process buffer immediately to free memory
        process_buffer(buffer)
        buffers.pop()  # Remove from list to allow garbage collection

    return buffers
```

### Batch Operations

```python
# For batch operations, reuse the scene object
scene = vvisf.CreateISFSceneRef()

for shader_file in shader_files:
    scene.use_file(shader_file)
    buffer = scene.create_and_render_a_buffer(size)
    # Process buffer
```

### Context Management

```python
# For advanced users, you can manage OpenGL contexts manually
# This is usually not necessary for most use cases

# context = vvisf.VVGL.CreateNewGLContextRef()
# scene = vvisf.CreateISFSceneRefUsing(context)
# ... use scene ...
# scene.prepare_to_be_deleted()
```

## GLBuffer and Image Handling

### GLBuffer Class

The `GLBuffer` class represents an OpenGL texture buffer and provides methods for image conversion.

#### Creation

```python
# Create from PIL Image
from PIL import Image
image = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
buffer = vvisf.GLBuffer.from_pil_image(image)

# Create from GLBufferPool
pool = vvisf.GLBufferPool()
buffer = pool.create_buffer(vvisf.Size(100, 100))
```

#### Properties

```python
# Basic properties
print(f"Size: {buffer.size}")
print(f"Texture ID: {buffer.name}")
print(f"Description: {buffer.get_description_string()}")

# Buffer type information
print(f"Type: {buffer.desc.type}")
print(f"Target: {buffer.desc.target}")
print(f"Internal Format: {buffer.desc.internalFormat}")
print(f"Pixel Format: {buffer.desc.pixelFormat}")
```

#### Image Conversion

```python
# Convert from PIL Image (working)
buffer = vvisf.GLBuffer.from_pil_image(pil_image)

# Convert to PIL Image (experimental - may have issues)
try:
    pil_image = buffer.to_pil_image()
except RuntimeError as e:
    print(f"Texture reading failed: {e}")
    # Fallback: create a new PIL Image with the same size
    pil_image = Image.new('RGBA', (buffer.size.width, buffer.size.height))
```

#### Buffer Methods

```python
# Check buffer properties
is_full = buffer.is_full_frame()
is_pot = buffer.is_pot2d_tex()  # Power of 2 texture
is_npot = buffer.is_npot2d_tex()  # Non-power of 2 texture

# Get buffer description
desc = buffer.get_description_string()
```

### GLBufferPool Class

The `GLBufferPool` class provides efficient buffer management and reuse.

#### Usage

```python
# Create a buffer pool
pool = vvisf.GLBufferPool()

# Create buffers of different sizes
buffer1 = pool.create_buffer(vvisf.Size(100, 100))
buffer2 = pool.create_buffer(vvisf.Size(200, 150))
buffer3 = pool.create_buffer(vvisf.Size(512, 512))

# Buffers are automatically managed by the pool
print(f"Buffer 1: {buffer1.size}")
print(f"Buffer 2: {buffer2.size}")
print(f"Buffer 3: {buffer3.size}")
```

### VVGL::Size Class

The `Size` class represents 2D dimensions.

#### Usage

```python
# Create sizes
size1 = vvisf.Size()  # Default: 0x0
size2 = vvisf.Size(1920, 1080)  # HD resolution
size3 = vvisf.Size(3840, 2160)  # 4K resolution

# Access properties
print(f"Width: {size2.width}")
print(f"Height: {size2.height}")

# String representation
print(f"Size: {size2}")  # "Size(1920, 1080)"
```

### Context Management

All GLBuffer operations require an OpenGL context to be current. The bindings automatically manage this using GLFW.

```python
# The context is automatically managed, but you can check platform info
platform = vvisf.get_platform_info()
print(f"Platform: {platform}")  # "GLFW (VVGL_SDK_GLFW)"

# Multiple operations work seamlessly
buffers = []
for i in range(5):
    image = Image.new('RGBA', (100, 100), (i * 50, 0, 0, 255))
    buffer = vvisf.GLBuffer.from_pil_image(image)
    buffers.append(buffer)
```

## Platform Support

### Supported Platforms

- **macOS**: Full support with GLFW backend
- **Linux**: Full support with GLFW backend (X11)
- **Windows**: Full support with GLFW backend (Win32)

### Platform-Specific Notes

#### macOS

```python
# On macOS, the bindings use GLFW for OpenGL context creation
# This works in both GUI and headless environments

import vvisf_bindings as vvisf
print(vvisf.get_platform_info())  # "GLFW (VVGL_SDK_GLFW)"
```

#### Linux

```python
# On Linux, ensure DISPLAY is set for GUI environments
# For headless rendering, use Xvfb or similar

import os
if not os.environ.get('DISPLAY'):
    print("Warning: DISPLAY not set. Headless rendering may not work.")
```

#### Windows

```python
# On Windows, the bindings work with both GUI and console applications
# No special configuration required
```

### Troubleshooting Platform Issues

```python
def check_platform_compatibility():
    """Check if the current platform supports VVISF."""
    try:
        import vvisf_bindings as vvisf

        if not vvisf.is_vvisf_available():
            print("VVISF is not available on this platform")
            return False

        print(f"Platform: {vvisf.get_platform_info()}")
        print("VVISF is available and working")
        return True

    except ImportError as e:
        print(f"Failed to import VVISF bindings: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Usage
if check_platform_compatibility():
    print("Platform is compatible")
else:
    print("Platform compatibility issues detected")
```

## Platform Abstraction and Fallbacks

The Python API provides robust platform abstraction:

- **Platform checks**: Use `isf_shader_renderer.platform.get_platform_info()` to get a summary of platform capabilities (OpenGL, VVISF, GLFW, headless support, etc).
- **Context management**: Use `get_context_manager()` to ensure the OpenGL context is current before buffer/image operations.
- **Fallbacks**: If VVISF, OpenGL, or GLFW are not available, the system automatically uses a fallback image generator. This ensures your code will always produce an image, even on unsupported systems.

### Example: Querying Platform Info

```python
from isf_shader_renderer.platform import get_platform_info
info = get_platform_info()
print(info.get_summary())
```

### Fallback Behavior

If the system cannot use VVISF (e.g., missing OpenGL or GLFW), the renderer will generate a placeholder image (animated gradient) instead of raising an error. This makes the API robust for headless, CI, or unsupported environments.

## Best Practices

### Code Organization

```python
class ISFRenderer:
    """High-level wrapper for ISF rendering."""

    def __init__(self):
        self.scene = vvisf.CreateISFSceneRef()
        self.current_shader = None

    def load_shader(self, shader_path):
        """Load a shader file."""
        try:
            self.scene.use_file(shader_path)
            self.current_shader = shader_path
            return True
        except vvisf.VVISFError as e:
            print(f"Error loading shader: {e}")
            return False

    def render_frame(self, size=(1920, 1080), time=None):
        """Render a single frame."""
        if not self.current_shader:
            raise RuntimeError("No shader loaded")

        render_size = vvisf.VVGL.Size(size[0], size[1])

        if time is not None:
            return self.scene.create_and_render_a_buffer(render_size, time)
        else:
            return self.scene.create_and_render_a_buffer(render_size)

    def set_parameter(self, name, value):
        """Set a shader parameter."""
        if isinstance(value, float):
            self.scene.set_value_for_input_named(vvisf.ISFFloatVal(value), name)
        elif isinstance(value, int):
            self.scene.set_value_for_input_named(vvisf.ISFLongVal(value), name)
        elif isinstance(value, bool):
            self.scene.set_value_for_input_named(vvisf.ISFBoolVal(value), name)
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            self.scene.set_value_for_input_named(vvisf.ISFPoint2DVal(value[0], value[1]), name)
        elif isinstance(value, (list, tuple)) and len(value) == 4:
            self.scene.set_value_for_input_named(vvisf.ISFColorVal(*value), name)
        else:
            raise ValueError(f"Unsupported value type for parameter {name}")

# Usage
renderer = ISFRenderer()
renderer.load_shader("shaders/example.fs")
renderer.set_parameter("intensity", 0.7)
buffer = renderer.render_frame()
```

### Error Handling

```python
def robust_shader_rendering(shader_path, parameters=None, size=(1920, 1080)):
    """Robust shader rendering with comprehensive error handling."""
    try:
        # Validate inputs
        if not os.path.exists(shader_path):
            raise FileNotFoundError(f"Shader file not found: {shader_path}")

        # Create scene
        scene = vvisf.CreateISFSceneRef()

        # Load shader
        scene.use_file(shader_path)

        # Set parameters
        if parameters:
            for name, value in parameters.items():
                try:
                    scene.set_value_for_input_named(value, name)
                except Exception as e:
                    print(f"Warning: Failed to set parameter {name}: {e}")

        # Render
        render_size = vvisf.VVGL.Size(size[0], size[1])
        buffer = scene.create_and_render_a_buffer(render_size)

        return buffer

    except vvisf.VVISFError as e:
        print(f"VVISF error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Performance Features

### Render Caching
- The renderer automatically caches rendered frames in memory based on shader, inputs, time, and size.
- If you render the same frame again, the cached image is used, improving performance for batch and repeated jobs.

### Custom Uniform Support
- All ISF input types are supported: bool, int, float, point2D, color, image.
- Input values from config or CLI are automatically coerced to the correct type (e.g., "true" to bool, "0.5,0.5" to point2D, file path to image).
- Invalid or mismatched values will raise a clear error.

#### Example: Using Image and Custom Uniform Inputs

```python
shader_config = ShaderConfig(
    input="shaders/complex.fs",
    output="output/frame.png",
    times=[0.0],
    width=512,
    height=512,
    inputs={
        "inputImage": "input/photo.png",  # image input
        "myBool": "true",
        "myInt": 42,
        "myFloat": 3.14,
        "myPoint": "0.25,0.75",
        "myColor": [0.9, 0.8, 0.7, 1.0]
    }
)
```

## Buffer Pooling and Reuse

The ShaderRenderer uses a GLBufferPool to efficiently reuse OpenGL buffers for rendering frames of the same size. This reduces memory allocations and improves performance, especially for batch or repeated rendering jobs.

- Buffers are allocated from the pool when rendering frames.
- The pool is automatically managed by the renderer; users do not need to interact with it directly.
- All buffer/image operations require the OpenGL context to be current (handled by the renderer).
- Direct allocation from the pool in user code may not yield a valid OpenGL texture outside the rendering pipeline.

**Benefits:**
- Reduces memory churn and allocation overhead.
- Improves performance for batch rendering.
- Ensures efficient use of GPU resources.

**Caveats:**
- Direct use of GLBufferPool outside the renderer may not always produce valid buffers (e.g., `name == 0`).
- Always use the renderer's API for rendering and image extraction.

This documentation provides a comprehensive guide to using the VVISF Python bindings. For more advanced usage and examples, refer to the test files in the `tests/` directory.
