"""MCP handlers for ISF shader operations."""

import base64
import sys
import tempfile
import traceback
from io import StringIO
from pathlib import Path
from typing import Dict, Any, List, Optional

from .models import RenderRequest, RenderResponse, ValidateRequest, ValidateResponse, GetShaderInfoRequest, GetShaderInfoResponse, Resource
from ..renderer import ShaderRenderer
from ..config import ShaderRendererConfig
from .utils import encode_image_to_base64


class ISFShaderHandlers:
    """Handlers for MCP requests."""
    
    def __init__(self):
        """Initialize handlers with default configuration."""
        self.config = ShaderRendererConfig()
        self.renderer = ShaderRenderer(self.config)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls."""
        if name == "render_shader":
            return await self._render_shader(arguments)
        elif name == "validate_shader":
            return await self._validate_shader(arguments)
        elif name == "get_shader_info":
            return await self._get_shader_info(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _render_shader(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle shader rendering requests."""
        # Capture stdout/stderr for logging
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        try:
            # Parse request
            request = RenderRequest(**arguments)
            
            # Validate shader first
            if not self.renderer.validate_shader(request.shader_content):
                # Try to get detailed error information by attempting to render
                error_info = None
                detailed_message = "Shader validation failed"
                
                try:
                    # This should fail and give us detailed error info
                    self.renderer.render_frame(
                        request.shader_content,
                        0.0,
                        Path("/tmp/test_error.png")
                    )
                except RuntimeError as e:
                    if isinstance(e.args[0], dict):
                        error_info = e.args[0]
                        # Extract meaningful error message for AI
                        if "message" in error_info:
                            detailed_message = error_info["message"]
                        elif "details" in error_info:
                            detailed_message = str(error_info["details"])
                    else:
                        error_info = {
                            "type": type(e).__name__,
                            "message": str(e),
                            "error_code": None,
                            "details": None,
                            "traceback": traceback.format_exc()
                        }
                        detailed_message = str(e)
                except Exception as e:
                    error_info = {
                        "type": type(e).__name__,
                        "message": str(e),
                        "error_code": None,
                        "details": None,
                        "traceback": traceback.format_exc()
                    }
                    detailed_message = str(e)
                
                # Create AI-friendly error message
                ai_message = self._format_error_message_for_ai(detailed_message, error_info)
                
                response = {
                    "success": False,
                    "message": ai_message,
                    "content": [],
                    "metadata": {},
                    "logs": [f"ERROR: {detailed_message}"],
                    "shader_info": None
                }
                
                if error_info:
                    response["error_details"] = error_info
                
                return response
            
            # Create output directory for this render session
            import tempfile
            import os
            from datetime import datetime
            
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"/tmp/isf_renderer/{session_id}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Render frames
            content = []
            rendered_files = []
            rendered_frames = []
            
            for i, time_code in enumerate(request.time_codes):
                # Create output file path (use PNG)
                filename = f"frame_{i:03d}_t{time_code:.2f}.png"
                output_path = output_dir / filename
                
                # Render frame
                self.renderer.render_frame(
                    request.shader_content,
                    time_code,
                    output_path
                )
                
                # Check file size
                file_size = output_path.stat().st_size
                rendered_files.append({
                    "path": str(output_path),
                    "filename": filename,
                    "size": file_size,
                    "time_code": time_code
                })
                # Add to rendered_frames as base64
                rendered_frames.append(encode_image_to_base64(output_path))
                # Add to content as file reference
                content.append({
                    "type": "text",
                    "text": f"Rendered frame saved to: {output_path} (size: {file_size} bytes)"
                })
            
            # Get captured logs
            logs = []
            stdout_logs = stdout_capture.getvalue()
            stderr_logs = stderr_capture.getvalue()
            if stdout_logs:
                logs.extend(stdout_logs.splitlines())
            if stderr_logs:
                logs.extend(stderr_logs.splitlines())
            
            # Extract shader info
            shader_info = self.renderer.get_shader_info(request.shader_content)
            
            # Return file-based response
            return {
                "success": True,
                "message": f"Successfully rendered {len(rendered_files)} frames to {output_dir}",
                "rendered_frames": rendered_frames,
                "metadata": {
                    "time_codes": request.time_codes,
                    "dimensions": f"{request.width}x{request.height}",
                    "quality": request.quality,
                    "frame_count": len(rendered_files),
                    "output_directory": str(output_dir),
                    "rendered_files": rendered_files
                },
                "logs": logs,
                "shader_info": shader_info
            }
            
        except Exception as e:
            error_info = {
                "type": type(e).__name__,
                "message": str(e),
            }
            if hasattr(e, 'error_code'):
                error_info["error_code"] = getattr(e, 'error_code')
            if hasattr(e, 'details'):
                error_info["details"] = getattr(e, 'details')
            error_info["traceback"] = traceback.format_exc()
            
            # Create AI-friendly error message
            ai_message = self._format_error_message_for_ai(str(e), error_info)
            
            return {
                "success": False,
                "message": ai_message,
                "content": [],
                "metadata": {},
                "logs": [f"ERROR: {str(e)}"],
                "shader_info": None,
                "error_details": error_info
            }
        finally:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    async def _validate_shader(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle shader validation requests."""
        try:
            # Parse request
            request = ValidateRequest(**arguments)
            
            # Validate shader
            is_valid = self.renderer.validate_shader(request.shader_content)
            
            # Extract shader info
            shader_info = self.renderer.get_shader_info(request.shader_content)
            
            # Basic validation checks
            errors = []
            warnings = []
            
            if not request.shader_content.strip():
                errors.append("Shader content is empty")
            
            if not is_valid:
                errors.append("Shader validation failed")
                # Try to get detailed error information
                try:
                    # This should fail and give us detailed error info
                    self.renderer.render_frame(
                        request.shader_content,
                        0.0,
                        Path("/tmp/test_error.png")
                    )
                except RuntimeError as e:
                    if isinstance(e.args[0], dict):
                        error_info = e.args[0]
                    else:
                        error_info = {
                            "type": type(e).__name__,
                            "message": str(e),
                            "error_code": None,
                            "details": None,
                            "traceback": traceback.format_exc()
                        }
                except Exception as e:
                    error_info = {
                        "type": type(e).__name__,
                        "message": str(e),
                        "error_code": None,
                        "details": None,
                        "traceback": traceback.format_exc()
                    }
                else:
                    error_info = None
            else:
                error_info = None
            
            # Check for common ISF elements
            content_upper = request.shader_content.upper()
            if "TIME" not in content_upper:
                warnings.append("No TIME uniform found - shader may not animate")
            
            if "RENDERSIZE" not in content_upper:
                warnings.append("No RENDERSIZE uniform found - shader may not be responsive")
            
            response = ValidateResponse(
                success=is_valid and not errors,
                message="Shader validation completed",
                shader_info=shader_info,
                errors=errors,
                warnings=warnings
            ).model_dump()
            
            if error_info:
                response["error_details"] = error_info
            
            return response
            
        except Exception as e:
            error_info = {
                "type": type(e).__name__,
                "message": str(e),
            }
            if hasattr(e, 'error_code'):
                error_info["error_code"] = getattr(e, 'error_code')
            if hasattr(e, 'details'):
                error_info["details"] = getattr(e, 'details')
            error_info["traceback"] = traceback.format_exc()
            # Create AI-friendly error message
            ai_message = self._format_error_message_for_ai(str(e), error_info)
            
            return ValidateResponse(
                success=False,
                message=ai_message,
                shader_info=None,
                errors=[str(e)],
                warnings=[]
            ).model_dump() | {"error_details": error_info}
    
    async def _get_shader_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle shader info extraction requests."""
        try:
            # Parse request
            request = GetShaderInfoRequest(**arguments)
            
            # Extract shader info (full ISF metadata)
            shader_info = self.renderer.get_shader_info(request.shader_content)
            
            return GetShaderInfoResponse(
                success=True,
                message="Shader information extracted successfully",
                shader_info=shader_info,
                errors=[]
            ).model_dump()
            
        except Exception as e:
            error_info = {
                "type": type(e).__name__,
                "message": str(e),
            }
            if hasattr(e, 'error_code'):
                error_info["error_code"] = getattr(e, 'error_code')
            if hasattr(e, 'details'):
                error_info["details"] = getattr(e, 'details')
            error_info["traceback"] = traceback.format_exc()
            # Create AI-friendly error message
            ai_message = self._format_error_message_for_ai(str(e), error_info)
            
            return GetShaderInfoResponse(
                success=False,
                message=ai_message,
                shader_info=None,
                errors=[str(e)]
            ).model_dump() | {"error_details": error_info}
    
    async def list_resources(self) -> List[Resource]:
        """List available resources (shader examples)."""
        resources = [
            Resource(
                uri="isf://examples/basic",
                name="Basic ISF Shader Example",
                description="A simple ISF shader example with basic color output"
            ),
            Resource(
                uri="isf://examples/animated",
                name="Animated ISF Shader Example", 
                description="An animated ISF shader example with time-based animation"
            ),
            Resource(
                uri="isf://examples/gradient",
                name="Gradient ISF Shader Example",
                description="A gradient-based ISF shader example"
            )
        ]
        return resources
    
    async def read_resource(self, uri: str) -> bytes:
        """Read resource content (shader examples)."""
        # Convert URI to string if it's an AnyUrl object
        uri_str = str(uri)
        if uri_str == "isf://examples/basic":
            return self._get_basic_shader_example().encode()
        elif uri_str == "isf://examples/animated":
            return self._get_animated_shader_example().encode()
        elif uri_str == "isf://examples/gradient":
            return self._get_gradient_shader_example().encode()
        else:
            raise ValueError(f"Unknown resource: {uri_str}")
    
    def _get_basic_shader_example(self) -> str:
        """Get basic shader example."""
        return """/*{
    "DESCRIPTION": "Basic ISF Shader Example",
    "CREDIT": "Generated by ISF Shader Renderer",
    "CATEGORIES": ["Basic"],
    "INPUTS": [],
    "PASSES": [
        {
            "TARGET": "bufferVariableA",
            "PERSISTENT": true,
            "FLOAT": true
        }
    ]
}*/

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    vec3 color = vec3(uv.x, uv.y, 0.5);
    gl_FragColor = vec4(color, 1.0);
}"""
    
    def _get_animated_shader_example(self) -> str:
        """Get animated shader example."""
        return """/*{
    "DESCRIPTION": "Animated ISF Shader Example",
    "CREDIT": "Generated by ISF Shader Renderer",
    "CATEGORIES": ["Animation"],
    "INPUTS": [],
    "PASSES": [
        {
            "TARGET": "bufferVariableA",
            "PERSISTENT": true,
            "FLOAT": true
        }
    ]
}*/

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    
    // Create animated wave pattern
    float wave = sin(uv.x * 10.0 + TIME * 2.0) * 0.5 + 0.5;
    wave += sin(uv.y * 8.0 + TIME * 1.5) * 0.5 + 0.5;
    
    vec3 color = vec3(wave, wave * 0.5, wave * 0.8);
    gl_FragColor = vec4(color, 1.0);
}"""
    
    def _get_gradient_shader_example(self) -> str:
        """Get gradient shader example."""
        return """/*{
    "DESCRIPTION": "Gradient ISF Shader Example",
    "CREDIT": "Generated by ISF Shader Renderer",
    "CATEGORIES": ["Gradient"],
    "INPUTS": [],
    "PASSES": [
        {
            "TARGET": "bufferVariableA",
            "PERSISTENT": true,
            "FLOAT": true
        }
    ]
}*/

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    
    // Create radial gradient
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(uv, center);
    
    vec3 color = vec3(1.0 - dist, dist, 0.5);
    gl_FragColor = vec4(color, 1.0);
}"""
    
    def _format_error_message_for_ai(self, error_message: str, error_info: Optional[Dict[str, Any]]) -> str:
        """
        Format error messages to be more helpful for AI users.
        
        Args:
            error_message: The raw error message
            error_info: Detailed error information dictionary
            
        Returns:
            Formatted error message suitable for AI consumption
        """
        # Handle common ISF validation errors
        if "ISF metadata" in error_message:
            if "validation errors for ISFInput" in error_message:
                # Extract specific validation errors
                if "min" in error_message.lower() and "max" in error_message.lower():
                    return ("ISF metadata validation error: MIN and MAX values for point2D inputs should be single numbers, not arrays. "
                           "For point2D inputs like 'uOffset', remove the MIN/MAX fields or use single numeric values. "
                           "Example: Remove 'MIN': [-1.0, -1.0] and 'MAX': [1.0, 1.0] from the uOffset input definition.")
                
                return ("ISF metadata validation error: One or more input parameters have invalid MIN/MAX values. "
                       "Check that MIN and MAX values match the input TYPE (float inputs need single numbers, not arrays).")
            
            return ("ISF metadata validation error: The JSON header in the shader contains invalid input definitions. "
                   "Check that all INPUTS have valid TYPE, DEFAULT, MIN, and MAX values according to ISF specification.")
        
        # Handle GLSL compilation errors
        if "GLSL" in error_message or "compilation" in error_message:
            return ("GLSL compilation error: The shader code contains syntax errors or invalid GLSL constructs. "
                   "Check for missing semicolons, undefined variables, or invalid function calls in the shader code.")
        
        # Handle missing main function
        if "main function" in error_message.lower():
            return ("Shader structure error: The shader is missing a 'void main()' function. "
                   "Every ISF shader must have a main function that sets gl_FragColor.")
        
        # Handle missing gl_FragColor
        if "gl_FragColor" in error_message.lower():
            return ("Shader output error: The shader does not assign a value to gl_FragColor. "
                   "Every ISF shader must set gl_FragColor in the main function.")
        
        # Handle empty content
        if "empty" in error_message.lower():
            return ("Shader content error: The shader content is empty or contains only whitespace. "
                   "Please provide valid ISF shader code with a JSON header and main function.")
        
        # Handle ISF header errors
        if "ISF header" in error_message.lower():
            return ("ISF header error: The shader does not have a valid ISF JSON header. "
                   "ISF shaders should start with a JSON block like /*{ ... }*/ containing metadata.")
        
        # Generic error with suggestions
        return (f"Shader error: {error_message}. "
               "Common issues include: invalid ISF metadata, GLSL syntax errors, missing main function, "
               "or incorrect input parameter definitions. Check the shader code and ISF specification.") 