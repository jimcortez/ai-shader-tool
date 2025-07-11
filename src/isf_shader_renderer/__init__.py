"""ISF Shader Renderer - A tool for rendering ISF shaders to PNG images."""

__version__ = "0.1.0"
__author__ = "Jim Cortez"
__email__ = "jim.cortez@gmail.com"

from .config import ShaderRendererConfig, load_config
from .renderer import ShaderRenderer

__all__ = ["ShaderRendererConfig", "load_config", "ShaderRenderer"]
