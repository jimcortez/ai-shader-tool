"""ISF shader rendering functionality using pyvvisf."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pyvvisf
from PIL import Image

from .config import ShaderConfig, ShaderRendererConfig

# Force logger to print INFO-level logs to stdout
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

logger = logging.getLogger(__name__)


class ShaderRenderer:
    """Main renderer class for ISF shaders using VVISF."""

    def __init__(self, config: ShaderRendererConfig):
        """Initialize the renderer with configuration."""
        self.config = config
        self._current_shader: Optional[str] = None

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
            time_code: Time offset for the shader (for animated shaders)
            output_path: Path to save the rendered image
            shader_config: Optional shader-specific configuration
        """
        # Get render dimensions
        width, height = self._get_dimensions(shader_config)

        # Render using the new ISFRenderer class
        try:
            with pyvvisf.ISFRenderer(shader_content) as renderer:
                # Set shader inputs if provided
                self._set_shader_inputs(renderer, shader_config, time_code, width, height)

                # Render the frame
                buffer = renderer.render(width, height, time_offset=time_code)

                # Convert buffer to PIL Image and save
                image = buffer.to_pil_image()
                if image is None:
                    raise RuntimeError(
                        "Failed to render: image is None (buffer conversion failed)"
                    )

                # Create output directory if needed
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Save the image
                image.save(output_path, quality=self._get_quality(shader_config))

                logger.info(f"Successfully rendered frame to {output_path}")

        except Exception as e:
            logger.error(f"Failed to render frame: {e}")
            error_info = {
                "type": type(e).__name__,
                "message": str(e),
            }
            if hasattr(e, 'error_code'):
                error_info["error_code"] = getattr(e, 'error_code')
            if hasattr(e, 'details'):
                error_info["details"] = getattr(e, 'details')
            import traceback
            error_info["traceback"] = traceback.format_exc()
            raise RuntimeError(error_info)

    def _set_shader_inputs(
        self,
        renderer,
        shader_config: Optional[ShaderConfig],
        time_code: float,
        width: int,
        height: int
    ) -> None:
        """Set shader input values using the ISFRenderer instance from render_frame."""
        try:
            # Set shader-specific inputs from config
            if shader_config and shader_config.inputs:
                for input_name, input_value in shader_config.inputs.items():
                    try:
                        # Handle different input types based on the new API's auto-coercion
                        if isinstance(input_value, str):
                            # Try to parse string values appropriately
                            if input_value.lower() in ("true", "1", "yes", "on"):
                                renderer.set_input(input_name, True)
                            elif input_value.lower() in ("false", "0", "no", "off"):
                                renderer.set_input(input_name, False)
                            elif "," in input_value or " " in input_value:
                                # Try to parse as tuple/list
                                try:
                                    # Remove spaces and split by comma
                                    parts = [float(x.strip()) for x in input_value.replace(" ", ",").split(",")]
                                    if len(parts) == 2:
                                        renderer.set_input(input_name, (parts[0], parts[1]))
                                    elif len(parts) == 3:
                                        renderer.set_input(input_name, (parts[0], parts[1], parts[2]))
                                    elif len(parts) == 4:
                                        renderer.set_input(input_name, (parts[0], parts[1], parts[2], parts[3]))
                                    else:
                                        # Try as float
                                        renderer.set_input(input_name, float(input_value))
                                except ValueError:
                                    # Try as float
                                    renderer.set_input(input_name, float(input_value))
                            else:
                                # Try as number first, then as string
                                try:
                                    if "." in input_value:
                                        renderer.set_input(input_name, float(input_value))
                                    else:
                                        renderer.set_input(input_name, int(input_value))
                                except ValueError:
                                    # Keep as string
                                    renderer.set_input(input_name, input_value)
                        else:
                            # The new ISFRenderer handles auto-coercion automatically for Python primitives
                            renderer.set_input(input_name, input_value)
                    except Exception as e:
                        logger.warning(f"Failed to set input '{input_name}': {e}")

            # Note: TIME and RENDERSIZE are handled automatically by ISFRenderer
            # when calling render() with time_offset parameter

        except Exception as e:
            logger.error(f"Failed to set shader inputs: {e}")

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

    def validate_shader(self, shader_content: str) -> bool:
        """
        Validate ISF shader content.

        Args:
            shader_content: The ISF shader source code

        Returns:
            True if the shader is valid, False otherwise
        """
        try:
            # Use ISFRenderer to validate the shader and GLSL compilation
            with pyvvisf.ISFRenderer(shader_content) as renderer:
                if hasattr(renderer, 'is_valid') and not renderer.is_valid():
                    return False
                # Check if shader has a main function
                if (
                    "void main(" not in shader_content
                    and "void main (" not in shader_content
                ):
                    logger.warning("Shader validation failed: missing main function")
                    return False
                # Try to render a minimal frame to trigger GLSL compilation
                try:
                    renderer.render(8, 8, time_offset=0.0)
                except Exception as glsl_error:
                    logger.warning(f"Shader validation failed: GLSL error: {glsl_error}")
                    return False
                return True
        except Exception as e:
            logger.error(f"Shader validation failed: {e}")
            error_info = {
                "type": type(e).__name__,
                "message": str(e),
            }
            if hasattr(e, 'error_code'):
                error_info["error_code"] = getattr(e, 'error_code')
            if hasattr(e, 'details'):
                error_info["details"] = getattr(e, 'details')
            import traceback
            error_info["traceback"] = traceback.format_exc()
            return False

    def get_shader_info(self, shader_content: str) -> Dict[str, Any]:
        """
        Extract information from ISF shader.

        Args:
            shader_content: The ISF shader source code

        Returns:
            Dictionary containing shader information (full ISF metadata if available)
        """
        def normalize_isf_metadata_keys(d):
            # Map ISF JSON keys to lowercase, e.g. DESCRIPTION -> description
            if not isinstance(d, dict):
                return d
            mapping = {
                "DESCRIPTION": "description",
                "CREDIT": "credit",
                "CATEGORIES": "categories",
                "INPUTS": "inputs",
                "PASSES": "passes",
            }
            out = {mapping.get(k, k.lower()): v for k, v in d.items()}
            # Always provide description and credit keys (even if None)
            if "description" not in out:
                out["description"] = None
            if "credit" not in out:
                out["credit"] = None
            return out

        try:
            # Use ISFRenderer to get shader information
            with pyvvisf.ISFRenderer(shader_content) as renderer:
                info = None
                if hasattr(renderer, 'get_shader_info'):
                    info = renderer.get_shader_info()
                if info is None:
                    info = {}
                info.update({
                    "size": len(shader_content),
                    "lines": len(shader_content.splitlines()),
                })
                norm = normalize_isf_metadata_keys(info)
                # If description is None, try fallback manual parsing
                if norm.get("description") is None:
                    import re, json
                    match = re.search(r'/\*\{([\s\S]*?)\}\*/', shader_content)
                    if match:
                        meta_str = '{' + match.group(1) + '}'
                        try:
                            meta = json.loads(meta_str)
                            fallback = normalize_isf_metadata_keys(meta)
                            if fallback.get("description"):
                                norm["description"] = fallback["description"]
                            if fallback.get("credit"):
                                norm["credit"] = fallback["credit"]
                        except Exception as ex:
                            logger.warning(f"Failed to parse ISF JSON block: {ex}")
                return norm
        except Exception as e:
            # Try to parse ISF JSON block manually (robust regex)
            import re, json
            match = re.search(r'/\*\{([\s\S]*?)\}\*/', shader_content)
            if match:
                meta_str = '{' + match.group(1) + '}'
                try:
                    meta = json.loads(meta_str)
                    out = normalize_isf_metadata_keys(meta)
                    return out
                except Exception as ex:
                    logger.warning(f"Failed to parse ISF JSON block: {ex}")
            logger.warning(f"Failed to extract shader info: {e}")
            error_info = {
                "type": type(e).__name__,
                "message": str(e),
            }
            if hasattr(e, 'error_code'):
                error_info["error_code"] = getattr(e, 'error_code')
            if hasattr(e, 'details'):
                error_info["details"] = getattr(e, 'details')
            import traceback
            error_info["traceback"] = traceback.format_exc()
            return {
                "type": "ISF",
                "size": len(shader_content),
                "lines": len(shader_content.splitlines()),
                "description": None,
                "credit": None,
                "error": error_info,
            }

    def cleanup(self) -> None:
        """Clean up resources."""
        # Note: ISFRenderer handles its own cleanup via context manager
        logger.info("Cleanup completed.")
