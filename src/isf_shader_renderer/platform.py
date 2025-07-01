"""Platform abstraction and fallback management for ISF shader rendering."""

import os
import sys
import platform
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class PlatformInfo:
    """Platform information and capabilities."""
    
    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine()
        self.processor = platform.processor()
        self.python_version = sys.version_info
        self.is_64bit = sys.maxsize > 2**32
        
        # Platform-specific flags
        self.is_macos = self.system == "Darwin"
        self.is_linux = self.system == "Linux"
        self.is_windows = self.system == "Windows"
        self.is_apple_silicon = self.is_macos and self.machine == "arm64"
        self.is_x86_64 = self.machine in ("x86_64", "AMD64")
        
        # Graphics capabilities
        self.opengl_available = False
        self.glfw_available = False
        self.vvisf_available = False
        self.headless_capable = False
        
        # Initialize capabilities
        self._detect_capabilities()
    
    def _detect_capabilities(self) -> None:
        """Detect platform capabilities."""
        try:
            # Check for VVISF bindings
            import isf_shader_renderer.vvisf_bindings as vvisf
            self.vvisf_available = vvisf.is_vvisf_available()
            self.opengl_available = self.vvisf_available
            self.glfw_available = self.vvisf_available
            
            # Get platform info from VVISF
            if self.vvisf_available:
                platform_info = vvisf.get_platform_info()
                logger.debug(f"VVISF platform info: {platform_info}")
                
                # Check for headless capability
                self.headless_capable = "GLFW" in platform_info
                
        except ImportError:
            logger.warning("VVISF bindings not available")
            self.vvisf_available = False
            self.opengl_available = False
            self.glfw_available = False
            self.headless_capable = False
        
        # Additional platform-specific checks
        if self.is_macos:
            self._check_macos_capabilities()
        elif self.is_linux:
            self._check_linux_capabilities()
        elif self.is_windows:
            self._check_windows_capabilities()
    
    def _check_macos_capabilities(self) -> None:
        """Check macOS-specific capabilities."""
        # macOS has good OpenGL support
        if not self.opengl_available:
            logger.warning("OpenGL not available on macOS - check Xcode installation")
        
        # Check for Metal support (future enhancement)
        # self.metal_available = self._check_metal_support()
    
    def _check_linux_capabilities(self) -> None:
        """Check Linux-specific capabilities."""
        # Check for X11/wayland display
        display = os.environ.get('DISPLAY')
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        
        if not display and not wayland_display:
            logger.info("No display detected - running in headless mode")
            self.headless_capable = True
        
        # Check for OpenGL libraries
        if not self.opengl_available:
            logger.warning("OpenGL not available on Linux - check graphics drivers")
    
    def _check_windows_capabilities(self) -> None:
        """Check Windows-specific capabilities."""
        # Windows typically has good OpenGL support
        if not self.opengl_available:
            logger.warning("OpenGL not available on Windows - check graphics drivers")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get platform summary for logging/debugging."""
        return {
            "system": self.system,
            "machine": self.machine,
            "processor": self.processor,
            "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
            "is_64bit": self.is_64bit,
            "is_apple_silicon": self.is_apple_silicon,
            "is_x86_64": self.is_x86_64,
            "opengl_available": self.opengl_available,
            "glfw_available": self.glfw_available,
            "vvisf_available": self.vvisf_available,
            "headless_capable": self.headless_capable,
        }
    
    def is_supported(self) -> bool:
        """Check if the current platform is supported."""
        # Basic platform support
        if not any([self.is_macos, self.is_linux, self.is_windows]):
            return False
        
        # Architecture support
        if not any([self.is_x86_64, self.is_apple_silicon]):
            return False
        
        return True
    
    def get_recommended_renderer(self) -> str:
        """Get the recommended renderer for this platform."""
        if self.vvisf_available and self.opengl_available:
            return "vvisf"
        else:
            return "placeholder"
    
    def get_error_message(self) -> Optional[str]:
        """Get error message if platform is not supported."""
        if self.is_supported():
            return None
        
        if not any([self.is_macos, self.is_linux, self.is_windows]):
            return f"Unsupported operating system: {self.system}"
        
        if not any([self.is_x86_64, self.is_apple_silicon]):
            return f"Unsupported architecture: {self.machine}"
        
        return "Unknown platform compatibility issue"


class ContextManager:
    """OpenGL context management helper."""
    
    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._context_initialized = False
    
    def ensure_context(self) -> bool:
        """Ensure OpenGL context is available and current."""
        if not self.platform_info.vvisf_available:
            logger.warning("VVISF not available, cannot ensure OpenGL context")
            return False
        
        try:
            import isf_shader_renderer.vvisf_bindings as vvisf
            
            # VVISF automatically manages GLFW context
            # Just check if it's available
            if vvisf.is_vvisf_available():
                self._context_initialized = True
                return True
            else:
                logger.error("VVISF available but context initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to ensure OpenGL context: {e}")
            return False
    
    def is_context_ready(self) -> bool:
        """Check if OpenGL context is ready for rendering."""
        return self._context_initialized and self.platform_info.vvisf_available
    
    def cleanup_context(self) -> None:
        """Clean up OpenGL context resources."""
        if self._context_initialized:
            try:
                import isf_shader_renderer.vvisf_bindings as vvisf
                # VVISF handles context cleanup automatically
                self._context_initialized = False
                logger.debug("OpenGL context cleaned up")
            except Exception as e:
                logger.warning(f"Error during context cleanup: {e}")


class FallbackManager:
    """Manages fallback rendering when VVISF is not available."""
    
    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.fallback_reason = None
    
    def should_use_fallback(self) -> bool:
        """Determine if fallback rendering should be used."""
        if not self.platform_info.vvisf_available:
            self.fallback_reason = "VVISF not available"
            return True
        
        if not self.platform_info.opengl_available:
            self.fallback_reason = "OpenGL not available"
            return True
        
        if not self.platform_info.glfw_available:
            self.fallback_reason = "GLFW not available"
            return True
        
        return False
    
    def get_fallback_reason(self) -> Optional[str]:
        """Get the reason for using fallback rendering."""
        return self.fallback_reason
    
    def create_fallback_image(self, width: int, height: int, time_code: float) -> bytes:
        """Create a fallback image when VVISF is not available."""
        try:
            from PIL import Image
            import numpy as np
            
            # Create a simple animated gradient
            x = np.linspace(0, 1, width)
            y = np.linspace(0, 1, height)
            X, Y = np.meshgrid(x, y)
            
            # Time-based animation
            r = np.sin(X * 10 + time_code * 2) * 0.5 + 0.5
            g = np.cos(Y * 8 + time_code * 1.5) * 0.5 + 0.5
            b = np.sin((X + Y) * 5 + time_code * 3) * 0.5 + 0.5
            
            # Combine channels
            rgb = np.stack([r, g, b], axis=2)
            rgb = (rgb * 255).astype(np.uint8)
            
            # Convert to PIL Image and save to bytes
            image = Image.fromarray(rgb, mode='RGB')
            import io
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except ImportError:
            # If PIL is not available, create a minimal fallback
            logger.warning("PIL not available for fallback rendering")
            return self._create_minimal_fallback(width, height)
    
    def _create_minimal_fallback(self, width: int, height: int) -> bytes:
        """Create a minimal fallback image without PIL."""
        # Create a simple 1x1 pixel PNG (minimal valid PNG)
        # This is a fallback for when even PIL is not available
        minimal_png = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\x0d'  # IHDR chunk length
            b'IHDR'              # IHDR chunk type
            b'\x00\x00\x00\x01'  # Width: 1
            b'\x00\x00\x00\x01'  # Height: 1
            b'\x08'              # Bit depth: 8
            b'\x02'              # Color type: RGB
            b'\x00'              # Compression: deflate
            b'\x00'              # Filter: none
            b'\x00'              # Interlace: none
            b'\x37\x6e\xf9\x24'  # IHDR CRC
            b'\x00\x00\x00\x0c'  # IDAT chunk length
            b'IDAT'              # IDAT chunk type
            b'\x78\x9c\x63\x00\x00\x00\x02\x00\x01'  # Compressed data (1 red pixel)
            b'\x00\x00\x00\x00'  # IDAT CRC
            b'\x00\x00\x00\x00'  # IEND chunk length
            b'IEND'              # IEND chunk type
            b'\xae\x42\x60\x82'  # IEND CRC
        )
        return minimal_png


def get_platform_info() -> PlatformInfo:
    """Get platform information singleton."""
    if not hasattr(get_platform_info, '_instance'):
        get_platform_info._instance = PlatformInfo()
    return get_platform_info._instance


def get_context_manager() -> ContextManager:
    """Get context manager singleton."""
    if not hasattr(get_context_manager, '_instance'):
        platform_info = get_platform_info()
        get_context_manager._instance = ContextManager(platform_info)
    return get_context_manager._instance


def get_fallback_manager() -> FallbackManager:
    """Get fallback manager singleton."""
    if not hasattr(get_fallback_manager, '_instance'):
        platform_info = get_platform_info()
        get_fallback_manager._instance = FallbackManager(platform_info)
    return get_fallback_manager._instance


def check_platform_compatibility() -> Tuple[bool, Optional[str]]:
    """Check if the current platform is compatible with the renderer."""
    platform_info = get_platform_info()
    
    if not platform_info.is_supported():
        return False, platform_info.get_error_message()
    
    return True, None


def get_recommended_configuration() -> Dict[str, Any]:
    """Get recommended configuration for the current platform."""
    platform_info = get_platform_info()
    
    config = {
        "renderer": platform_info.get_recommended_renderer(),
        "headless": platform_info.headless_capable,
        "fallback_available": True,
    }
    
    # Platform-specific recommendations
    if platform_info.is_macos:
        config.update({
            "opengl_version": "4.1",
            "metal_support": False,  # Future enhancement
        })
    elif platform_info.is_linux:
        config.update({
            "opengl_version": "3.3",
            "x11_support": "DISPLAY" in os.environ,
            "wayland_support": "WAYLAND_DISPLAY" in os.environ,
        })
    elif platform_info.is_windows:
        config.update({
            "opengl_version": "4.0",
            "directx_support": False,  # Future enhancement
        })
    
    return config 