"""ISF shader rendering functionality using pyvvisf."""

import hashlib
import json
import logging
import time
import traceback
import tracemalloc
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
        self._scene = None
        self._current_shader: Optional[str] = None
        self._render_cache = {}  # (hash) -> PIL Image

        # Initialize GLBufferPool for buffer reuse
        self._buffer_pool = None
        try:
            self._buffer_pool = pyvvisf.GLBufferPool()
            logger.info("GLBufferPool initialized for buffer reuse.")
        except Exception as e:
            logger.warning(f"Failed to initialize GLBufferPool: {e}")

    def _make_render_cache_key(self, shader_content, inputs, time_code, width, height):
        # Serialize all relevant parameters to a hashable string
        key_data = {
            "shader": shader_content,
            "inputs": inputs,
            "time": time_code,
            "width": width,
            "height": height,
        }
        key_json = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_json.encode("utf-8")).hexdigest()

    def render_frame(
        self,
        shader_content: str,
        time_code: float,
        output_path: Path,
        shader_config: Optional[ShaderConfig] = None,
        profile: bool = False,
    ) -> None:
        """
        Render a single frame of an ISF shader.

        Args:
            shader_content: The ISF shader source code
            time_code: The time code for this frame
            output_path: Path where the output image should be saved
            shader_config: Optional shader-specific configuration
            profile: If True, log timing and memory usage for each stage
        """
        # Validate shader before rendering
        if not self.validate_shader(shader_content):
            raise RuntimeError(
                "Shader validation failed: shader is invalid. No image will be generated."
            )
        try:
            timings = {}
            if profile:
                tracemalloc.start()
                t0 = time.perf_counter()

            # Get dimensions
            width, height = self._get_dimensions(shader_config)
            if profile:
                timings["dimensions"] = time.perf_counter() - t0
                t1 = time.perf_counter()

            # Prepare cache key
            inputs = (
                shader_config.inputs if shader_config and shader_config.inputs else {}
            )
            cache_key = self._make_render_cache_key(
                shader_content, inputs, time_code, width, height
            )

            # Check cache
            if cache_key in self._render_cache:
                image = self._render_cache[cache_key]
                output_path.parent.mkdir(parents=True, exist_ok=True)
                quality = self._get_quality(shader_config)
                image.save(output_path, "PNG", optimize=True, quality=quality)
                logger.debug(f"Used cached render for {output_path}")
                if profile:
                    timings["cache"] = time.perf_counter() - t1
                    current, peak = tracemalloc.get_traced_memory()
                    logger.info(
                        f"[PROFILE] cache hit: timings={timings}, mem={current/1024:.1f}KB, peak={peak/1024:.1f}KB"
                    )
                    tracemalloc.stop()
                return
            if profile:
                timings["cache"] = time.perf_counter() - t1
                t2 = time.perf_counter()

            # Ensure shader is loaded
            self._ensure_shader_loaded(shader_content)
            if profile:
                timings["shader_load"] = time.perf_counter() - t2
                t3 = time.perf_counter()

            # Set shader inputs
            self._set_shader_inputs(shader_config, time_code)
            if profile:
                timings["inputs"] = time.perf_counter() - t3
                t4 = time.perf_counter()

            # Clean up buffer pool before each render to prevent texture state issues
            if self._buffer_pool is not None:
                try:
                    self._buffer_pool.cleanup()
                    logger.info("[DEBUG] Buffer pool cleaned up before render")
                except Exception as cleanup_exc:
                    logger.warning(f"[DEBUG] Buffer pool cleanup failed: {cleanup_exc}")

            # Force reinitialize OpenGL context before each render
            try:
                pyvvisf.reinitialize_glfw_context()
                gl_info = pyvvisf.get_gl_info()
                logger.info(
                    f"[DEBUG] OpenGL/GLFW context info before render: {gl_info}"
                )
                print(f"[DEBUG] OpenGL/GLFW context info before render: {gl_info}")
            except Exception as ctx_exc:
                logger.error(
                    f"[DEBUG] Failed to reinitialize OpenGL context: {ctx_exc}"
                )
                print(f"[DEBUG] Failed to reinitialize OpenGL context: {ctx_exc}")

            # Render the frame
            if self._scene:
                size = pyvvisf.Size(width, height)

                # Always use direct scene buffer creation for batch rendering stability
                buffer = None
                try:
                    buffer = self._scene.create_and_render_a_buffer(size)
                    logger.info(
                        f"[DEBUG] Buffer from scene: name={getattr(buffer, 'name', None)}, size={getattr(buffer, 'size', None)}"
                    )
                    print(
                        f"[DEBUG] Buffer from scene: name={getattr(buffer, 'name', None)}, size={getattr(buffer, 'size', None)}"
                    )

                    # Validate buffer
                    if buffer is None:
                        raise RuntimeError("Scene returned None buffer")
                    if getattr(buffer, "name", 0) == 0:
                        raise RuntimeError("Buffer has invalid OpenGL texture name=0")

                except Exception as render_exc:
                    logger.error(f"[ERROR] Render failed: {render_exc}")
                    print(f"[ERROR] Render failed: {render_exc}")
                    raise RuntimeError(f"Failed to render frame: {render_exc}")

                if profile:
                    timings["buffer_alloc+render"] = time.perf_counter() - t4
                    t5 = time.perf_counter()

                # Convert buffer to PIL Image and save
                image = self._buffer_to_pil_image(buffer)
                if image is None:
                    logger.error(
                        f"[DEBUG] Buffer to PIL image conversion failed for buffer: {buffer}"
                    )
                    print(
                        f"[DEBUG] Buffer to PIL image conversion failed for buffer: {buffer}"
                    )
                    raise RuntimeError(
                        "Failed to render: image is None (buffer conversion failed)"
                    )
                if profile:
                    timings["to_pil_image"] = time.perf_counter() - t5
                    t6 = time.perf_counter()

                # Save the image
                output_path.parent.mkdir(parents=True, exist_ok=True)
                quality = self._get_quality(shader_config)
                image.save(output_path, "PNG", optimize=True, quality=quality)
                if profile:
                    timings["save"] = time.perf_counter() - t6

                # Store in cache
                self._render_cache[cache_key] = image

                logger.debug(f"Rendered frame to {output_path}")
                logger.info(
                    f"[DEBUG] Successfully rendered and saved image to {output_path}"
                )
                print(f"[DEBUG] Successfully rendered and saved image to {output_path}")
                if profile:
                    current, peak = tracemalloc.get_traced_memory()
                    logger.info(
                        f"[PROFILE] timings={timings}, mem={current/1024:.1f}KB, peak={peak/1024:.1f}KB"
                    )
                    tracemalloc.stop()
            else:
                raise RuntimeError("No scene available for rendering")

        except Exception as e:
            logger.error(f"Rendering failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            raise

    def _ensure_shader_loaded(self, shader_content: str) -> None:
        """Ensure the shader is loaded in the scene."""
        if self._current_shader != shader_content:
            try:
                # Create new scene and load shader
                self._scene = pyvvisf.CreateISFSceneRef()

                # Create ISFDoc from shader content
                doc = pyvvisf.CreateISFDocRefWith(shader_content)
                self._scene.use_doc(doc)

                self._current_shader = shader_content
                logger.debug("Loaded new shader")
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f"Failed to load shader: {e}\n{tb}")
                self._scene = None
                raise RuntimeError(f"Failed to initialize ISF scene: {e}\n{tb}")

    def _set_shader_inputs(
        self, shader_config: Optional[ShaderConfig], time_code: float
    ) -> None:
        """Set shader input values."""
        if not self._scene:
            return

        try:
            # Set time-based inputs
            self._scene.set_value_for_input_named(
                pyvvisf.ISFFloatVal(time_code), "TIME"
            )

            # Set resolution inputs
            width, height = self._get_dimensions(shader_config)
            self._scene.set_value_for_input_named(
                pyvvisf.ISFFloatVal(float(width)), "RENDERSIZE.x"
            )
            self._scene.set_value_for_input_named(
                pyvvisf.ISFFloatVal(float(height)), "RENDERSIZE.y"
            )

            # Set shader-specific inputs from config
            if shader_config and shader_config.inputs:
                for input_name, input_value in shader_config.inputs.items():
                    self._set_input_value(input_name, input_value)
        except Exception as e:
            logger.error(f"Failed to set shader inputs: {e}")

    def _set_input_value(self, input_name: str, input_value: Any) -> None:
        """Set a single input value based on its type, including image inputs and validation."""
        if not self._scene:
            return

        try:
            # Get input type from ISFDoc
            doc = self._scene.doc() if hasattr(self._scene, "doc") else None
            input_type = None
            if doc:
                # Find the ISFAttr with the matching name
                for attr in doc.inputs():
                    if (
                        callable(getattr(attr, "name", None))
                        and attr.name() == input_name
                    ):
                        input_type = str(attr.type())
                        break
                else:
                    available = [
                        attr.name()
                        for attr in doc.inputs()
                        if callable(getattr(attr, "name", None))
                    ]
                    logger.warning(
                        f"Input '{input_name}' not found in ISFDoc inputs. Available: {available}"
                    )

            # Validate and coerce value to expected type
            def coerce(val, typ):
                if typ == "ISFValType_Bool":
                    if isinstance(val, bool):
                        return pyvvisf.ISFBoolVal(val)
                    if isinstance(val, str):
                        if val.lower() in ("true", "1", "yes", "on"):
                            return pyvvisf.ISFBoolVal(True)
                        if val.lower() in ("false", "0", "no", "off"):
                            return pyvvisf.ISFBoolVal(False)
                    raise ValueError(
                        f"Cannot coerce {val!r} to bool for input '{input_name}'"
                    )
                elif typ == "ISFValType_Long":
                    try:
                        return pyvvisf.ISFLongVal(int(val))
                    except Exception:
                        raise ValueError(
                            f"Cannot coerce {val!r} to int for input '{input_name}'"
                        )
                elif typ == "ISFValType_Float":
                    try:
                        return pyvvisf.ISFFloatVal(float(val))
                    except Exception:
                        raise ValueError(
                            f"Cannot coerce {val!r} to float for input '{input_name}'"
                        )
                elif typ == "ISFValType_Point2D":
                    if isinstance(val, (list, tuple)) and len(val) == 2:
                        return pyvvisf.ISFPoint2DVal(float(val[0]), float(val[1]))
                    if isinstance(val, str):
                        parts = [float(x) for x in val.replace(",", " ").split()]
                        if len(parts) == 2:
                            return pyvvisf.ISFPoint2DVal(parts[0], parts[1])
                    raise ValueError(
                        f"Cannot coerce {val!r} to Point2D for input '{input_name}'"
                    )
                elif typ == "ISFValType_Color":
                    if isinstance(val, (list, tuple)) and len(val) == 4:
                        return pyvvisf.ISFColorVal(
                            float(val[0]), float(val[1]), float(val[2]), float(val[3])
                        )
                    if isinstance(val, str):
                        parts = [float(x) for x in val.replace(",", " ").split()]
                        if len(parts) == 4:
                            return pyvvisf.ISFColorVal(
                                parts[0], parts[1], parts[2], parts[3]
                            )
                    raise ValueError(
                        f"Cannot coerce {val!r} to Color (4 floats) for input '{input_name}'"
                    )
                elif typ == "ISFValType_Image":
                    if isinstance(val, str):
                        from PIL import Image

                        img = Image.open(val).convert("RGBA")
                        glbuf = pyvvisf.GLBuffer.from_pil_image(img)
                        if self._scene is not None:
                            self._scene.set_buffer_for_input_named(glbuf, input_name)
                        return None  # Buffer set directly
                    raise ValueError(
                        f"Cannot coerce {val!r} to image file path for input '{input_name}'"
                    )
                else:
                    logger.warning(
                        f"Unknown or unsupported ISF input type '{typ}' for '{input_name}'"
                    )
                    return None

            if input_type:
                norm_type = input_type.replace(".", "_")
                result = coerce(input_value, norm_type)
                if result is not None and self._scene is not None:
                    self._scene.set_value_for_input_named(result, input_name)
                return

            # Fallback: try to infer type as before
            if isinstance(input_value, bool):
                val = pyvvisf.ISFBoolVal(input_value)
            elif isinstance(input_value, int):
                val = pyvvisf.ISFLongVal(input_value)
            elif isinstance(input_value, float):
                val = pyvvisf.ISFFloatVal(input_value)
            elif isinstance(input_value, (list, tuple)) and len(input_value) == 2:
                val = pyvvisf.ISFPoint2DVal(
                    float(input_value[0]), float(input_value[1])
                )
            elif isinstance(input_value, (list, tuple)) and len(input_value) == 4:
                val = pyvvisf.ISFColorVal(
                    float(input_value[0]),
                    float(input_value[1]),
                    float(input_value[2]),
                    float(input_value[3]),
                )
            else:
                logger.warning(
                    f"Unknown input type for {input_name}: {type(input_value)}"
                )
                return
            if self._scene is not None:
                self._scene.set_value_for_input_named(val, input_name)
        except Exception as e:
            logger.warning(f"Failed to set input {input_name}: {e}")

    def _buffer_to_pil_image(self, buffer) -> Image.Image:
        """Convert VVISF buffer to PIL Image."""
        try:
            # Try to convert buffer to PIL Image
            if hasattr(buffer, "to_pil_image"):
                return buffer.to_pil_image()
            else:
                # Fallback: create a new PIL Image with buffer dimensions
                size = buffer.size
                return buffer.create_pil_image("RGBA", (255, 255, 255, 255))
        except Exception as e:
            logger.warning(f"Failed to convert buffer to PIL Image: {e}")
            # Create a fallback image
            if hasattr(buffer, "size"):
                size = buffer.size
                return Image.new(
                    "RGBA", (int(size.width), int(size.height)), (255, 0, 0, 255)
                )
            else:
                return Image.new("RGBA", (1920, 1080), (255, 0, 0, 255))

    def _get_dimensions(self, shader_config: Optional[ShaderConfig]) -> Tuple[int, int]:
        """Get render dimensions from config, enforcing max texture size."""
        if shader_config:
            width = shader_config.get_width(self.config.defaults)
            height = shader_config.get_height(self.config.defaults)
        else:
            width = self.config.defaults.width
            height = self.config.defaults.height
        # Enforce max texture size
        max_size = getattr(self.config.defaults, "max_texture_size", 4096)
        if width > max_size or height > max_size:
            logger.warning(
                f"Requested render size {width}x{height} exceeds max_texture_size {max_size}. Clamping to {max_size}."
            )
            width = min(width, max_size)
            height = min(height, max_size)
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
            # Try to create ISFDoc from shader content
            doc = pyvvisf.CreateISFDocRefWith(shader_content)
            if doc is None:
                return False

            # Check if shader has a main function
            if (
                "void main(" not in shader_content
                and "void main (" not in shader_content
            ):
                logger.warning("Shader validation failed: missing main function")
                return False

            return True
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
        try:
            # Create ISFDoc and extract detailed information
            doc = pyvvisf.CreateISFDocRefWith(shader_content)

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
        """Clean up resources: scene, buffer pool, render cache, and OpenGL context."""
        if self._scene:
            try:
                self._scene.prepare_to_be_deleted()
            except Exception as e:
                logger.warning(f"Error during scene cleanup: {e}")
            self._scene = None
        self._current_shader = None

        # Clear render cache
        if self._render_cache:
            self._render_cache.clear()
            logger.info("Render cache cleared.")

        # Release buffer pool
        if self._buffer_pool is not None:
            try:
                # Clean up buffer pool thoroughly
                if hasattr(self._buffer_pool, "cleanup"):
                    self._buffer_pool.cleanup()
                if hasattr(self._buffer_pool, "housekeeping"):
                    self._buffer_pool.housekeeping()
                if hasattr(self._buffer_pool, "purge"):
                    self._buffer_pool.purge()
                # Delete the reference
                self._buffer_pool = None
                logger.info("GLBufferPool cleaned up and released.")
            except Exception as e:
                logger.warning(f"Error during buffer pool cleanup: {e}")

        # Note: pyvvisf does not provide a cleanup method for OpenGL context
        # The context is managed internally by pyvvisf
        logger.info("Cleanup completed.")
