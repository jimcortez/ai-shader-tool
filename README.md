# AI Shader Tool

A Python-based tool for rendering ISF (Interactive Shader Format) shaders to images using the VVISF-GL library. Provides a command-line interface (CLI) and Python API for batch and automated shader rendering.

## Installation

See [documents/VVISF-GL_Build_and_Integration.md](documents/VVISF-GL_Build_and_Integration.md) for detailed build and setup instructions.

Basic steps:
```bash
git clone --recursive https://github.com/your-username/ai-shader-tool.git
cd ai-shader-tool
./scripts/setup.sh
```

## Quick Start: Command Line Usage

After building, use the CLI to render shaders:

```bash
python -m isf_shader_renderer.cli --input path/to/shader.fs --output output.png
```

### CLI Options
- `--input` / `-i`: Path to ISF shader file
- `--output` / `-o`: Output image path
- `--config` / `-c`: YAML config for batch rendering
- `--time` / `-t`: Time value for animation
- `--width` / `-w`: Output image width
- `--height` / `-h`: Output image height
- `--inputs`: Set shader input values (JSON or key=value)

**New Feature:**
If a shader fails to compile, you can now access detailed error logs from Python via the ISFDoc object. See [Python API documentation](documents/PYTHON_API.md#error-handling-and-fallbacks) for usage examples.

For full CLI usage and configuration examples, see [documents/PYTHON_API.md](documents/PYTHON_API.md#cli-usage) and [examples/config.yaml](examples/config.yaml).

## Documentation
- [Python API documentation](documents/PYTHON_API.md)
- [Build & Integration Guide](documents/VVISF-GL_Build_and_Integration.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [AI Coding Documentation](documents/ai-coding-documentation.md)

## License
MIT
