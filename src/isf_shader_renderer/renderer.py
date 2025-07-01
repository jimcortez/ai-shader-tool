"""ISF shader rendering functionality using VVISF bindings."""

import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging
import hashlib
import json

from PIL import Image

from .config import ShaderRendererConfig, ShaderConfig
from .platform import get_platform_info, get_context_manager, get_fallback_manager

logger = logging.getLogger(__name__)


class ShaderRenderer:
    """Main renderer class for ISF shaders using VVISF."""
    
    def __init__(self, config: ShaderRendererConfig):
        """Initialize the renderer with configuration."""
        self.config = config
        self._scene = None
        self._current_shader: Optional[str] = None
        self._render_cache = {}  # (hash) -> PIL Image
        
        # Initialize platform components
        self.platform_info = get_platform_info()
        self.context_manager = get_context_manager()
        self.fallback_manager = get_fallback_manager()
        
        # Initialize GLBufferPool for buffer reuse
        self._buffer_pool = None
        if self.platform_info.vvisf_available:
            try:
                import isf_shader_renderer.vvisf_bindings as vvisf
                self._buffer_pool = vvisf.GLBufferPool()
                logger.info("GLBufferPool initialized for buffer reuse.")
            except Exception as e:
                logger.warning(f"Failed to initialize GLBufferPool: {e}")
        
        # Check platform compatibility
        compatible, error_msg = self.platform_info.is_supported(), self.platform_info.get_error_message()
        if not compatible:
            logger.warning(f"Platform compatibility issue: {error_msg}")
        
        # Log platform summary
        logger.info(f"Platform: {self.platform_info.get_summary()}")
        
        if self.fallback_manager.should_use_fallback():
            logger.warning(f"Using fallback renderer: {self.fallback_manager.get_fallback_reason()}")
    
    def _make_render_cache_key(self, shader_content, inputs, time_code, width, height):
        # Serialize all relevant parameters to a hashable string
        key_data = {
            'shader': shader_content,
            'inputs': inputs,
            'time': time_code,
            'width': width,
            'height': height
        }
        key_json = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_json.encode('utf-8')).hexdigest()

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
        if self.fallback_manager.should_use_fallback():
            self._render_placeholder_frame(shader_content, time_code, output_path, shader_config)
            return
        
        try:
            # Ensure OpenGL context is ready
            if not self.context_manager.ensure_context():
                logger.warning("Failed to ensure OpenGL context, using fallback")
                self._render_placeholder_frame(shader_content, time_code, output_path, shader_config)
                return
            
            # Get dimensions
            width, height = self._get_dimensions(shader_config)
            
            # Prepare cache key
            inputs = shader_config.inputs if shader_config and shader_config.inputs else {}
            cache_key = self._make_render_cache_key(shader_content, inputs, time_code, width, height)
            
            # Check cache
            if cache_key in self._render_cache:
                image = self._render_cache[cache_key]
                output_path.parent.mkdir(parents=True, exist_ok=True)
                quality = self._get_quality(shader_config)
                image.save(output_path, "PNG", optimize=True, quality=quality)
                logger.debug(f"Used cached render for {output_path}")
                return
            
            # Ensure shader is loaded
            self._ensure_shader_loaded(shader_content)
            
            # Set shader inputs
            self._set_shader_inputs(shader_config, time_code)
            
            # Render the frame
            if self._scene:
                import isf_shader_renderer.vvisf_bindings as vvisf
                size = vvisf.Size(width, height)

                # Use buffer pool for allocation if available
                buffer = None
                if self._buffer_pool is not None:
                    buffer = self._buffer_pool.create_buffer(size)
                    # Render into the pooled buffer (if supported by VVISF)
                    # If not supported, fall back to scene's create_and_render_a_buffer
                    try:
                        buffer = self._scene.create_and_render_a_buffer(size, buffer)
                    except TypeError:
                        # If the method does not accept a buffer, fall back
                        buffer = self._scene.create_and_render_a_buffer(size)
                else:
                    buffer = self._scene.create_and_render_a_buffer(size)

                # Convert buffer to PIL Image and save
                image = self._buffer_to_pil_image(buffer)

                # Save the image
                output_path.parent.mkdir(parents=True, exist_ok=True)
                quality = self._get_quality(shader_config)
                image.save(output_path, "PNG", optimize=True, quality=quality)

                # Store in cache
                self._render_cache[cache_key] = image

                logger.debug(f"Rendered frame to {output_path}")
            else:
                raise RuntimeError("Scene not initialized")
            
        except Exception as e:
            logger.error(f"Failed to render frame: {e}")
            # Fallback to placeholder
            self._render_placeholder_frame(shader_content, time_code, output_path, shader_config)
    
    def _ensure_shader_loaded(self, shader_content: str) -> None:
        """Ensure the shader is loaded in the scene."""
        if self.fallback_manager.should_use_fallback():
            return
            
        if self._current_shader != shader_content:
            try:
                import isf_shader_renderer.vvisf_bindings as vvisf
                # Create new scene and load shader
                self._scene = vvisf.CreateISFSceneRef()
                
                # Create ISFDoc from shader content
                doc = vvisf.CreateISFDocRefWith(shader_content)
                self._scene.use_doc(doc)
                
                self._current_shader = shader_content
                logger.debug("Loaded new shader")
            except Exception as e:
                logger.error(f"Failed to load shader: {e}")
                self._scene = None
    
    def _set_shader_inputs(self, shader_config: Optional[ShaderConfig], time_code: float) -> None:
        """Set shader input values."""
        if self.fallback_manager.should_use_fallback() or not self._scene:
            return
        
        try:
            import isf_shader_renderer.vvisf_bindings as vvisf
            
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
        except Exception as e:
            logger.error(f"Failed to set shader inputs: {e}")
    
    def _set_input_value(self, input_name: str, input_value: Any) -> None:
        """Set a single input value based on its type, including image inputs and validation."""
        if self.fallback_manager.should_use_fallback() or not self._scene:
            return
        
        try:
            import isf_shader_renderer.vvisf_bindings as vvisf
            
            # Get input type from ISFDoc
            doc = self._scene.doc() if hasattr(self._scene, 'doc') else None
            input_type = None
            if doc:
                # Find the ISFAttr with the matching name
                for attr in doc.inputs():
                    if callable(getattr(attr, 'name', None)) and attr.name() == input_name:
                        input_type = str(attr.type())
                        break
                else:
                    available = [attr.name() for attr in doc.inputs() if callable(getattr(attr, 'name', None))]
                    logger.warning(f"Input '{input_name}' not found in ISFDoc inputs. Available: {available}")
            
            # Validate and coerce value to expected type
            def coerce(val, typ):
                if typ == 'ISFValType_Bool':
                    if isinstance(val, bool):
                        return vvisf.ISFBoolVal(val)
                    if isinstance(val, str):
                        if val.lower() in ('true', '1', 'yes', 'on'):
                            return vvisf.ISFBoolVal(True)
                        if val.lower() in ('false', '0', 'no', 'off'):
                            return vvisf.ISFBoolVal(False)
                    raise ValueError(f"Cannot coerce {val!r} to bool for input '{input_name}'")
                elif typ == 'ISFValType_Long':
                    try:
                        return vvisf.ISFLongVal(int(val))
                    except Exception:
                        raise ValueError(f"Cannot coerce {val!r} to int for input '{input_name}'")
                elif typ == 'ISFValType_Float':
                    try:
                        return vvisf.ISFFloatVal(float(val))
                    except Exception:
                        raise ValueError(f"Cannot coerce {val!r} to float for input '{input_name}'")
                elif typ == 'ISFValType_Point2D':
                    if isinstance(val, (list, tuple)) and len(val) == 2:
                        return vvisf.ISFPoint2DVal(float(val[0]), float(val[1]))
                    if isinstance(val, str):
                        parts = [float(x) for x in val.replace(',', ' ').split()]
                        if len(parts) == 2:
                            return vvisf.ISFPoint2DVal(parts[0], parts[1])
                    raise ValueError(f"Cannot coerce {val!r} to Point2D for input '{input_name}'")
                elif typ == 'ISFValType_Color':
                    if isinstance(val, (list, tuple)) and len(val) == 4:
                        return vvisf.ISFColorVal(float(val[0]), float(val[1]), float(val[2]), float(val[3]))
                    if isinstance(val, str):
                        parts = [float(x) for x in val.replace(',', ' ').split()]
                        if len(parts) == 4:
                            return vvisf.ISFColorVal(parts[0], parts[1], parts[2], parts[3])
                    raise ValueError(f"Cannot coerce {val!r} to Color (4 floats) for input '{input_name}'")
                elif typ == 'ISFValType_Image':
                    if isinstance(val, str):
                        from PIL import Image
                        img = Image.open(val).convert('RGBA')
                        glbuf = vvisf.GLBuffer.from_pil_image(img)
                        self._scene.set_buffer_for_input_named(glbuf, input_name)
                        return None  # Buffer set directly
                    raise ValueError(f"Cannot coerce {val!r} to image file path for input '{input_name}'")
                else:
                    logger.warning(f"Unknown or unsupported ISF input type '{typ}' for '{input_name}'")
                    return None
            
            if input_type:
                norm_type = input_type.replace('.', '_')
                result = coerce(input_value, norm_type)
                if result is not None:
                    self._scene.set_value_for_input_named(result, input_name)
                return
            
            # Fallback: try to infer type as before
            if isinstance(input_value, bool):
                val = vvisf.ISFBoolVal(input_value)
            elif isinstance(input_value, int):
                val = vvisf.ISFLongVal(input_value)
            elif isinstance(input_value, float):
                val = vvisf.ISFFloatVal(input_value)
            elif isinstance(input_value, (list, tuple)) and len(input_value) == 2:
                val = vvisf.ISFPoint2DVal(float(input_value[0]), float(input_value[1]))
            elif isinstance(input_value, (list, tuple)) and len(input_value) == 4:
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
        
        try:
            # Use fallback manager to create image
            image_data = self.fallback_manager.create_fallback_image(width, height, time_code)
            
            # Save the image data directly
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Created fallback image: {self.fallback_manager.get_fallback_reason()}")
            
        except Exception as e:
            logger.error(f"Fallback rendering failed: {e}")
            # Create a minimal fallback image
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
        if self.fallback_manager.should_use_fallback():
            # Basic validation when VVISF is not available
            return bool(shader_content.strip())
        
        try:
            import isf_shader_renderer.vvisf_bindings as vvisf
            # Try to create ISFDoc from shader content
            doc = vvisf.CreateISFDocRefWith(shader_content)
            return doc is not None
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
        if self.fallback_manager.should_use_fallback():
            # Basic info when VVISF is not available
            return {
                "type": "ISF",
                "size": len(shader_content),
                "placeholder": True,
                "fallback_reason": self.fallback_manager.get_fallback_reason(),
            }
        
        try:
            import isf_shader_renderer.vvisf_bindings as vvisf
            # Create ISFDoc and extract detailed information
            doc = vvisf.CreateISFDocRefWith(shader_content)
            
            info = {
                "type": "ISF",
                "name": doc.name,
                "description": doc.description,
                "credit": doc.credit,
                "version": doc.vsn,
                "file_type": str(doc.type),
                "categories": doc.categories,
                "size": len(shader_content),
                "lines": len(shader_content.splitlines()),
                "vvisf_available": True,
            }
            
            # Get input information
            info["inputs"] = []
            for attr in doc.inputs():
                input_info = {
                    "name": attr.name,
                    "type": str(attr.type()),
                    "description": attr.description,
                }
                info["inputs"].append(input_info)
            
            return info
            
        except Exception as e:
            logger.warning(f"Failed to extract shader info: {e}")
            return {
                "type": "ISF",
                "size": len(shader_content),
                "lines": len(shader_content.splitlines()),
                "vvisf_available": True,
                "error": str(e),
            }
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self._scene:
            try:
                self._scene.prepare_to_be_deleted()
            except Exception as e:
                logger.warning(f"Error during scene cleanup: {e}")
            self._scene = None
        self._current_shader = None
        
        # Clean up platform resources
        self.context_manager.cleanup_context() 