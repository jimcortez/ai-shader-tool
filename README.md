# ISF Shader Renderer

A Python-based tool for rendering ISF (Interactive Shader Format) shaders to images using the [pyvvisf](https://github.com/jimcortez/pyvvisf) library. Provides a command-line interface (CLI) and Python API for batch and automated shader rendering with AI-friendly output options.

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
git clone https://github.com/jecortez/ai-shader-tool.git
cd ai-shader-tool
pip install -e .
```

## Quick Start: Command Line Usage

### Basic Rendering

Render a single shader to an image:

```bash
isf-shader-render path/to/shader.fs --output output.png
```

### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Path to YAML configuration file for batch rendering |
| `--output` | `-o` | Output image path (required when not using config) |
| `--time` | `-t` | Time code for rendering (can be specified multiple times) |
| `--width` | `-w` | Output image width (default: 1920) |
| `--height` | `-h` | Output image height (default: 1080) |
| `--quality` | `-q` | PNG quality 1-100 (default: 95) |
| `--verbose` | `-v` | Enable verbose output |
| `--profile` | | Enable profiling (timing and memory usage) |
| `--info` | | Show renderer and shader information |
| `--ai-info` | | Format output for AI processing (natural language, no colors) |
| `--inputs` | | Shader input values as key=value pairs |

### AI-Friendly Output

Use the `--ai-info` flag for AI systems and automated processing:

```bash
# Normal output (with colors and status updates)
isf-shader-render shader.fs --output result.png

# AI-friendly output (natural language only)
isf-shader-render shader.fs --output result.png --ai-info
```

**AI-friendly output features:**
- Natural language error descriptions
- No terminal colors or formatting
- No progress bars or status updates
- Clear, actionable error messages
- Consistent format for AI parsing

### Batch Rendering

Render multiple shaders with different settings:

```bash
# Using configuration file
isf-shader-render --config config.yaml

# Using multiple time codes
isf-shader-render shader.fs --output frame_%04d.png --time 0 --time 1 --time 2
```

### Shader Inputs

Set shader input values:

```bash
# Set color input
isf-shader-render shader.fs --output result.png --inputs "color=1.0 0.0 0.0 1.0"

# Set multiple inputs
isf-shader-render shader.fs --output result.png --inputs "intensity=0.8,position=0.5 0.3,enabled=true"
```

### Error Handling Examples

The renderer provides helpful error messages:

```bash
# Missing main function
isf-shader-render invalid.fs --output result.png --ai-info
# Output: The shader is missing a main function. ISF shaders require a 'void main()' function to define the fragment shader entry point.

# Syntax error
isf-shader-render syntax_error.fs --output result.png --ai-info
# Output: The shader contains syntax errors: Unexpected token '}'. Please check the GLSL syntax and ensure all brackets, semicolons, and function calls are properly formatted.

# File not found
isf-shader-render missing.fs --output result.png --ai-info
# Output: File not found: missing.fs. Please check that the file path is correct and the file exists.
```

## Configuration Files

Use YAML configuration files for complex batch rendering:

```yaml
# config.yaml
defaults:
  width: 1920
  height: 1080
  quality: 95
  max_texture_size: 4096

shaders:
  - input: "shaders/red.fs"
    output: "output/red_%04d.png"
    times: [0.0, 1.0, 2.0]
    width: 1280
    height: 720
    inputs:
      intensity: 0.8
      color: [1.0, 0.0, 0.0, 1.0]

  - input: "shaders/blue.fs"
    output: "output/blue_%04d.png"
    times: [0.0, 0.5, 1.0, 1.5, 2.0]
    inputs:
      color: [0.0, 0.0, 1.0, 1.0]
```

## Platform Support

This tool uses the [pyvvisf](https://github.com/jimcortez/pyvvisf) library for high-performance ISF shader rendering:

- **macOS**: Full support (OpenGL, Metal)
- **Linux**: Full support (OpenGL)
- **Windows**: Full support (OpenGL)


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

## License

MIT License - see [LICENSE](LICENSE) file for details.

## ISF Shader Renderer MCP Server (AI Integration)

The ISF Shader Renderer includes a Model Context Protocol (MCP) server for programmatic shader rendering, validation, and information extraction. This enables integration with AI assistants (like Cursor) and other automated clients.

### Quick Start (MCP Server)

Install with MCP dependencies:
```bash
pip install isf-shader-renderer[mcp]
```

Start the MCP server (stdio mode, recommended for AI tools):
```bash
isf-mcp-server --stdio
```

Or start the HTTP server:
```bash
isf-mcp-server --http --port 8000
```
