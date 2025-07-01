"""ISF shader rendering functionality using VVISF bindings."""

import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging

from PIL import Image

from .config import Config, ShaderConfig

# Import VVISF bindings
try:
    import isf_shader_renderer.vvisf_bindings as vvisf
    VVISF_AVAILABLE = True
except ImportError:
    VVISF_AVAILABLE = False
    vvisf = None

logger = logging.getLogger(__name__)


class ShaderRenderer:
    """Main renderer class for ISF shaders using VVISF."""
    
    def __init__(self, config: Config):
        """Initialize the renderer with configuration."""
        self.config = config
        self._scene = None
        self._current_shader: Optional[str] = None
        
        if not VVISF_AVAILABLE:
            logger.warning("VVISF bindings not available, using placeholder renderer")
    
    def render_frame(
        self,
        shader_content: str,
        time_code: float,
        output_path: Path,
        shader_config: Optional[ShaderConfig] = None,
    ) -> None:
        """
        Render a single frame of an ISF shader.
        
        Args:
            shader_content: The ISF shader source code
            time_code: The time code for this frame
            output_path: Path where the output image should be saved
            shader_config: Optional shader-specific configuration
        """
        if not VVISF_AVAILABLE:
            self._render_placeholder_frame(shader_content, time_code, output_path, shader_config)
            return
        
        try:
            # Get dimensions
            width, height = self._get_dimensions(shader_config)
            
            # Ensure shader is loaded
            self._ensure_shader_loaded(shader_content)
            
            # Set shader inputs
            self._set_shader_inputs(shader_config, time_code)
            
            # Render the frame
            if vvisf and self._scene:
                size = vvisf.Size(width, height)
                buffer = self._scene.create_and_render_a_buffer(size)
                
                # Convert buffer to PIL Image and save
                image = self._buffer_to_pil_image(buffer)
                
                # Save the image
                output_path.parent.mkdir(parents=True, exist_ok=True)
                quality = self._get_quality(shader_config)
                image.save(output_path, "PNG", optimize=True, quality=quality)
                
                logger.debug(f"Rendered frame to {output_path}")
            else:
                raise RuntimeError("VVISF not available or scene not initialized")
            
        except Exception as e:
            logger.error(f"Failed to render frame: {e}")
            # Fallback to placeholder
            self._render_placeholder_frame(shader_content, time_code, output_path, shader_config)
    
    def _ensure_shader_loaded(self, shader_content: str) -> None:
        """Ensure the shader is loaded in the scene."""
        if not vvisf:
            return
            
        if self._current_shader != shader_content:
            # Create new scene and load shader
            self._scene = vvisf.CreateISFSceneRef()
            
            # Create ISFDoc from shader content
            doc = vvisf.CreateISFDocRefWith(shader_content)
            self._scene.use_doc(doc)
            
            self._current_shader = shader_content
            logger.debug("Loaded new shader")
    
    def _set_shader_inputs(self, shader_config: Optional[ShaderConfig], time_code: float) -> None:
        """Set shader input values."""
        if not vvisf or not self._scene:
            return
        
        # Set time-based inputs
        self._scene.set_value_for_input_named(vvisf.ISFFloatVal(time_code), "TIME")
        
        # Set resolution inputs
        width, height = self._get_dimensions(shader_config)
        self._scene.set_value_for_input_named(vvisf.ISFFloatVal(float(width)), "RENDERSIZE.x")
        self._scene.set_value_for_input_named(vvisf.ISFFloatVal(float(height)), "RENDERSIZE.y")
        
        # Set shader-specific inputs from config
        if shader_config and shader_config.inputs:
            for input_name, input_value in shader_config.inputs.items():
                self._set_input_value(input_name, input_value)
    
    def _set_input_value(self, input_name: str, input_value: Any) -> None:
        """Set a single input value based on its type."""
        if not vvisf or not self._scene:
            return
        
        try:
            # Determine input type and create appropriate ISFVal
            if isinstance(input_value, bool):
                val = vvisf.ISFBoolVal(input_value)
            elif isinstance(input_value, int):
                val = vvisf.ISFLongVal(input_value)
            elif isinstance(input_value, float):
                val = vvisf.ISFFloatVal(input_value)
            elif isinstance(input_value, (list, tuple)) and len(input_value) == 2:
                # 2D Point
                val = vvisf.ISFPoint2DVal(float(input_value[0]), float(input_value[1]))
            elif isinstance(input_value, (list, tuple)) and len(input_value) == 4:
                # Color (RGBA)
                val = vvisf.ISFColorVal(
                    float(input_value[0]), float(input_value[1]),
                    float(input_value[2]), float(input_value[3])
                )
            else:
                logger.warning(f"Unknown input type for {input_name}: {type(input_value)}")
                return
            
            self._scene.set_value_for_input_named(val, input_name)
            
        except Exception as e:
            logger.warning(f"Failed to set input {input_name}: {e}")
    
    def _buffer_to_pil_image(self, buffer) -> Image.Image:
        """Convert VVISF buffer to PIL Image."""
        try:
            # Try to convert buffer to PIL Image
            if hasattr(buffer, 'to_pil_image'):
                return buffer.to_pil_image()
            else:
                # Fallback: create a new PIL Image with buffer dimensions
                size = buffer.size
                return buffer.create_pil_image("RGBA", (255, 255, 255, 255))
        except Exception as e:
            logger.warning(f"Failed to convert buffer to PIL Image: {e}")
            # Create a fallback image
            if hasattr(buffer, 'size'):
                size = buffer.size
                return Image.new('RGBA', (int(size.width), int(size.height)), (255, 0, 0, 255))
            else:
                return Image.new('RGBA', (1920, 1080), (255, 0, 0, 255))
    
    def _get_dimensions(self, shader_config: Optional[ShaderConfig]) -> Tuple[int, int]:
        """Get render dimensions from config."""
        if shader_config:
            width = shader_config.get_width(self.config.defaults)
            height = shader_config.get_height(self.config.defaults)
        else:
            width = self.config.defaults.width
            height = self.config.defaults.height
        return width, height
    
    def _get_quality(self, shader_config: Optional[ShaderConfig]) -> int:
        """Get quality setting from config."""
        if shader_config:
            return shader_config.get_quality(self.config.defaults)
        return self.config.defaults.quality
    
    def _render_placeholder_frame(
        self,
        shader_content: str,
        time_code: float,
        output_path: Path,
        shader_config: Optional[ShaderConfig] = None,
    ) -> None:
        """Render a placeholder frame when VVISF is not available."""
        # Determine dimensions
        width, height = self._get_dimensions(shader_config)
        
        # Create a placeholder image
        image = self._create_placeholder_image(shader_content, time_code, width, height)
        
        # Save the image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        quality = self._get_quality(shader_config)
        image.save(output_path, "PNG", optimize=True, quality=quality)
    
    def _create_placeholder_image(
        self, shader_content: str, time_code: float, width: int, height: int
    ) -> Image.Image:
        """
        Create a placeholder image for development/testing.
        
        This method is used when VVISF is not available.
        """
        # Create a simple gradient based on time code
        import numpy as np
        
        # Create a gradient that changes over time
        x = np.linspace(0, 1, width)
        y = np.linspace(0, 1, height)
        X, Y = np.meshgrid(x, y)
        
        # Create a time-based animation
        r = np.sin(X * 10 + time_code * 2) * 0.5 + 0.5
        g = np.cos(Y * 8 + time_code * 1.5) * 0.5 + 0.5
        b = np.sin((X + Y) * 5 + time_code * 3) * 0.5 + 0.5
        
        # Combine channels
        rgb = np.stack([r, g, b], axis=2)
        rgb = (rgb * 255).astype(np.uint8)
        
        # Convert to PIL Image
        image = Image.fromarray(rgb)
        
        return image
    
    def validate_shader(self, shader_content: str) -> bool:
        """
        Validate ISF shader content.
        
        Args:
            shader_content: The ISF shader source code
            
        Returns:
            True if the shader is valid, False otherwise
        """
        if not VVISF_AVAILABLE:
            # Basic validation when VVISF is not available
            return bool(shader_content.strip())
        
        try:
            # Try to create ISFDoc from shader content
            if vvisf:
                doc = vvisf.CreateISFDocRefWith(shader_content)
                return True
            else:
                return False
        except Exception as e:
            logger.warning(f"Shader validation failed: {e}")
            return False
    
    def get_shader_info(self, shader_content: str) -> Dict[str, Any]:
        """
        Extract information from ISF shader.
        
        Args:
            shader_content: The ISF shader source code
            
        Returns:
            Dictionary containing shader information
        """
        if not VVISF_AVAILABLE:
            # Basic info when VVISF is not available
            return {
                "type": "ISF",
                "size": len(shader_content),
                "lines": len(shader_content.splitlines()),
                "has_time_uniform": "TIME" in shader_content.upper(),
                "has_resolution_uniform": "RENDERSIZE" in shader_content.upper(),
                "vvisf_available": False,
            }
        
        try:
            # Create ISFDoc and extract detailed information
            if not vvisf:
                raise RuntimeError("VVISF not available")
            doc = vvisf.CreateISFDocRefWith(shader_content)
            
            info = {
                "type": "ISF",
                "name": doc.name(),
                "description": doc.description(),
                "credit": doc.credit(),
                "version": doc.vsn(),
                "file_type": str(doc.type()),
                "categories": doc.categories(),
                "size": len(shader_content),
                "lines": len(shader_content.splitlines()),
                "vvisf_available": True,
            }
            
            # Get input information
            inputs = doc.inputs()
            info["inputs"] = []
            for input_attr in inputs:
                input_info = {
                    "name": input_attr.name(),
                    "type": str(input_attr.type()),
                    "description": input_attr.description(),
                    "label": input_attr.label(),
                }
                info["inputs"].append(input_info)
            
            # Get source code info
            info["fragment_source"] = doc.frag_shader_source()
            info["vertex_source"] = doc.vert_shader_source()
            
            return info
            
        except Exception as e:
            logger.warning(f"Failed to extract shader info: {e}")
            return {
                "type": "ISF",
                "size": len(shader_content),
                "lines": len(shader_content.splitlines()),
                "has_time_uniform": "TIME" in shader_content.upper(),
                "has_resolution_uniform": "RENDERSIZE" in shader_content.upper(),
                "vvisf_available": True,
                "error": str(e),
            }
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self._scene:
            self._scene.prepare_to_be_deleted()
            self._scene = None
        self._current_shader = None 