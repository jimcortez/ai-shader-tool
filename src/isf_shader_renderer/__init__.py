"""ISF Shader Renderer - A tool for rendering ISF shaders to PNG images."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .config import Config, load_config
from .renderer import ShaderRenderer

__all__ = ["Config", "load_config", "ShaderRenderer"] 