# ISF Shader Renderer

A Python command-line tool for rendering ISF (Interactive Shader Format) shaders to PNG images at specified time codes.

## Features

- Render ISF shaders to PNG images
- Support for multiple time codes in a single run
- YAML configuration file support
- Command-line overrides for configuration
- Input from files or stdin
- Configurable output resolution and quality
- Rich command-line interface with progress indicators

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/isf-shader-renderer.git
cd isf-shader-renderer
```

2. Install in development mode:
```bash
pip install -e .
```

3. Install development dependencies (optional):
```bash
pip install -e ".[dev]"
```

### From PyPI (when published)

```bash
pip install isf-shader-renderer
```

## Usage

### Basic Usage

Render a shader at a specific time:

```bash
isf-renderer --shader path/to/shader.fs --time 1.5 --output output.png
```

### Using Configuration File

Create a configuration file `config.yaml`:

```yaml
# Default settings
defaults:
  width: 1920
  height: 1080
  quality: 95

# Shader-specific settings
shaders:
  - input: "shaders/wave.fs"
    output: "output/wave_%04d.png"
    times: [0.0, 0.5, 1.0, 1.5, 2.0]
    width: 1280
    height: 720
```

Run with configuration:

```bash
isf-renderer --config config.yaml
```

### Command Line Options

```bash
isf-renderer [OPTIONS] COMMAND [ARGS]...

Options:
  --config PATH           Path to YAML configuration file
  --shader PATH           Path to ISF shader file (or use stdin)
  --time FLOAT            Time code for rendering (can be specified multiple times)
  --output PATH           Output file path
  --width INTEGER         Output width [default: 1920]
  --height INTEGER        Output height [default: 1080]
  --quality INTEGER       PNG quality (1-100) [default: 95]
  --help                  Show this message and exit
```

### Examples

Render multiple frames:
```bash
isf-renderer --shader animation.fs --time 0.0 --time 0.5 --time 1.0 --output frame_%04d.png
```

Read shader from stdin:
```bash
cat shader.fs | isf-renderer --time 1.0 --output output.png
```

Override configuration settings:
```bash
isf-renderer --config config.yaml --width 2560 --height 1440
```

## Configuration File Format

The YAML configuration file supports the following structure:

```yaml
# Global defaults
defaults:
  width: 1920
  height: 1080
  quality: 95
  output_format: "png"

# Shader definitions
shaders:
  - input: "path/to/shader1.fs"
    output: "output/shader1_%04d.png"
    times: [0.0, 0.5, 1.0]
    width: 1280  # Override default
    height: 720  # Override default
  
  - input: "path/to/shader2.fs"
    output: "output/shader2_%04d.png"
    times: [0.0, 1.0, 2.0, 3.0]
    # Use defaults for width/height
```

### Configuration Options

- `defaults`: Global settings applied to all shaders unless overridden
- `shaders`: List of shader configurations
  - `input`: Path to ISF shader file
  - `output`: Output file pattern (supports printf-style formatting)
  - `times`: List of time codes to render
  - `width`: Output width (optional, uses default if not specified)
  - `height`: Output height (optional, uses default if not specified)
  - `quality`: PNG quality (optional, uses default if not specified)

## Development

### Setup Development Environment

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

### Linting

```bash
flake8 src/ tests/
```

## Project Structure

```
isf-shader-renderer/
├── src/
│   └── isf_shader_renderer/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── config.py           # Configuration management
│       ├── renderer.py         # Shader rendering logic
│       └── utils.py            # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_renderer.py
├── examples/
│   ├── config.yaml
│   └── shaders/
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- ISF (Interactive Shader Format) specification
- Python community for excellent tooling and libraries

## Roadmap

- [ ] ISF shader parsing and validation
- [ ] OpenGL/WebGL rendering backend
- [ ] Support for shader uniforms and parameters
- [ ] Batch processing capabilities
- [ ] Video output support
- [ ] GUI interface
- [ ] Plugin system for custom renderers 