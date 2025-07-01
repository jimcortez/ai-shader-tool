"""Tests for shader rendering functionality."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from isf_shader_renderer.config import Config, ShaderConfig
from isf_shader_renderer.renderer import ShaderRenderer


class TestShaderRenderer:
    """Test ShaderRenderer class."""
    
    def test_renderer_creation(self):
        """Test creating ShaderRenderer."""
        config = Config()
        renderer = ShaderRenderer(config)
        assert renderer.config == config
    
    def test_render_frame_basic(self):
        """Test basic frame rendering."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        shader_content = "/* ISF shader */ void main() { gl_FragColor = vec4(1.0); }"
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            renderer.render_frame(shader_content, 1.0, output_path)
            
            # Check that file was created
            assert output_path.exists()
            
            # Check that it's a valid image
            image = Image.open(output_path)
            assert image.size == (1920, 1080)  # Default size
            assert image.mode == 'RGB'
        finally:
            output_path.unlink()
    
    def test_render_frame_with_shader_config(self):
        """Test frame rendering with shader-specific configuration."""
        config = Config()
        shader_config = ShaderConfig(
            input="test.fs",
            output="output.png",
            times=[0.0],
            width=640,
            height=480,
            quality=80,
        )
        config.shaders.append(shader_config)
        
        renderer = ShaderRenderer(config)
        shader_content = "/* ISF shader */ void main() { gl_FragColor = vec4(1.0); }"
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            renderer.render_frame(shader_content, 1.0, output_path, shader_config)
            
            # Check that file was created
            assert output_path.exists()
            
            # Check that it's a valid image with custom size
            image = Image.open(output_path)
            assert image.size == (640, 480)
            assert image.mode == 'RGB'
        finally:
            output_path.unlink()
    
    def test_validate_shader(self):
        """Test shader validation."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        # Valid shader
        valid_shader = "/* ISF shader */ void main() { gl_FragColor = vec4(1.0); }"
        assert renderer.validate_shader(valid_shader) is True
        
        # Empty shader
        assert renderer.validate_shader("") is False
        assert renderer.validate_shader("   ") is False
    
    def test_get_shader_info(self):
        """Test shader info extraction."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        shader_content = """
        /* ISF shader */
        uniform float TIME;
        uniform vec2 RENDERSIZE;
        void main() { 
            gl_FragColor = vec4(1.0); 
        }
        """
        
        info = renderer.get_shader_info(shader_content)
        
        assert info["type"] == "ISF"
        assert info["size"] > 0
        assert info["lines"] > 0
        assert info["has_time_uniform"] is True
        assert info["has_resolution_uniform"] is True
    
    def test_create_placeholder_image(self):
        """Test placeholder image creation."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        shader_content = "/* ISF shader */ void main() { gl_FragColor = vec4(1.0); }"
        image = renderer._create_placeholder_image(shader_content, 1.0, 100, 100)
        
        assert isinstance(image, Image.Image)
        assert image.size == (100, 100)
        assert image.mode == 'RGB'
    
    def test_render_frame_creates_directory(self):
        """Test that render_frame creates output directory if needed."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        shader_content = "/* ISF shader */ void main() { gl_FragColor = vec4(1.0); }"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "nested" / "output"
            output_path = output_dir / "test.png"
            
            renderer.render_frame(shader_content, 1.0, output_path)
            
            # Check that directory was created
            assert output_dir.exists()
            assert output_path.exists() 