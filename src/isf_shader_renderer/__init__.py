"""ISF Shader Renderer - A tool for rendering ISF shaders to PNG images."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .cli import main
from .config import ShaderRendererConfig, load_config
from .renderer import ShaderRenderer

__all__ = ["main", "ShaderRendererConfig", "load_config", "ShaderRenderer"] 