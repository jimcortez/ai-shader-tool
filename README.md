# AI Shader Tool

A Python-based tool for rendering ISF (Interactive Shader Format) shaders to images using the [pyvvisf](https://github.com/jimcortez/pyvvisf) library. Provides a command-line interface (CLI) and Python API for batch and automated shader rendering.

## Installation

### Prerequisites
- Python 3.8 or later
- OpenGL drivers and platform support

### Install from PyPI
```bash
pip install isf-shader-renderer
```

### Install from source
```bash
git clone https://github.com/your-username/ai-shader-tool.git
cd ai-shader-tool
pip install -e .
```

## Quick Start: Command Line Usage

Use the CLI to render shaders:

```bash
isf-renderer --input path/to/shader.fs --output output.png
```

### CLI Options
- `--input` / `-i`: Path to ISF shader file
- `--output` / `-o`: Output image path
- `--config` / `-c`: YAML config for batch rendering
- `--time` / `-t`: Time value for animation
- `--width` / `-w`: Output image width
- `--height` / `-h`: Output image height
- `--inputs`: Set shader input values (JSON or key=value)

**Features:**
- Automatic shader validation and error reporting
- Configurable `max_texture_size` to limit render dimensions (default: 4096)
- Support for all ISF input types (bool, int, float, point2d, color, image)
- Batch rendering with YAML configuration files

For full CLI usage and configuration examples, see [examples/config.yaml](examples/config.yaml).

## Python API Usage

```python
from isf_shader_renderer import ShaderRenderer, ShaderRendererConfig

# Create renderer
config = ShaderRendererConfig()
renderer = ShaderRenderer(config)

# Render a shader
shader_content = """
/*{
    "DESCRIPTION": "Simple color shader",
    "INPUTS": [
        {
            "NAME": "color",
            "TYPE": "color",
            "DEFAULT": [1.0, 0.0, 0.0, 1.0]
        }
    ]
}*/

void main() {
    gl_FragColor = INPUTS_color;
}
"""

renderer.render_frame(
    shader_content=shader_content,
    time_code=0.0,
    output_path="output.png"
)
```

## Dependencies

This tool uses the [pyvvisf](https://github.com/jimcortez/pyvvisf) library for high-performance ISF shader rendering. The library provides Python bindings for the VVISF-GL C++ library and supports:

- **macOS**: Full support (OpenGL, Metal)
- **Linux**: Full support (OpenGL)
- **Windows**: Full support (OpenGL)

## Platform Requirements

- OpenGL drivers and platform support
- Python 3.8+
- [pyvvisf](https://github.com/jimcortez/pyvvisf) (automatically installed as dependency)

## Examples

See the `examples/` directory for configuration and usage examples:

```bash
# Run the basic usage example
python examples/basic_usage.py
```

## Development and Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m regression  # Run regression tests
pytest -m stress     # Run stress tests

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=src/isf_shader_renderer
```

### Test Markers

The test suite includes specialized markers for different test categories:

- `@pytest.mark.regression`: Tests that prevent regressions of previously fixed bugs (segfaults, crashes)
- `@pytest.mark.stress`: Stress tests for stability (multiple renders, batch processing)
- `@pytest.mark.xfail`: Known failing tests that document current limitations

## License
MIT
