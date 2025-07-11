"""ISF Shader Renderer - A tool for rendering ISF shaders to PNG images."""

__version__ = "0.1.0"
__author__ = "Jim Cortez"
__email__ = "jim.cortez@gmail.com"

<<<<<<< HEAD
from .config import Config, load_config
from .renderer import ShaderRenderer

__all__ = ["Config", "load_config", "ShaderRenderer"] 
=======
from .cli import main
from .config import ShaderRendererConfig, load_config
from .renderer import ShaderRenderer

__all__ = ["main", "ShaderRendererConfig", "load_config", "ShaderRenderer"]
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
