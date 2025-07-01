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
        
        shader_content = """/*{
    \"DESCRIPTION\": \"Test shader\",
    \"CREDIT\": \"Test\",
    \"CATEGORIES\": [\"Test\"],
    \"INPUTS\": []
}*/
void main() { gl_FragColor = vec4(1.0); }"""
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            renderer.render_frame(shader_content, 1.0, output_path)
            
            # Check that file was created
            assert output_path.exists()
            
            # Check that it's a valid image
            image = Image.open(output_path)
            assert image.size == (1920, 1080)  # Default size
            assert image.mode == 'RGBA'
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
        shader_content = """/*{
    \"DESCRIPTION\": \"Test shader\",
    \"CREDIT\": \"Test\",
    \"CATEGORIES\": [\"Test\"],
    \"INPUTS\": []
}*/
void main() { gl_FragColor = vec4(1.0); }"""
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            renderer.render_frame(shader_content, 1.0, output_path, shader_config)
            
            # Check that file was created
            assert output_path.exists()
            
            # Check that it's a valid image with custom size
            image = Image.open(output_path)
            assert image.size == (640, 480)
            assert image.mode == 'RGBA'
        finally:
            output_path.unlink()
    
    def test_validate_shader(self):
        """Test shader validation."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        # Valid ISF shader
        valid_shader = """/*{
    "DESCRIPTION": "Test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() { 
    gl_FragColor = vec4(1.0); 
}"""
        assert renderer.validate_shader(valid_shader) is True
        
        # Empty shader
        assert renderer.validate_shader("") is False
        assert renderer.validate_shader("   ") is False
    
    def test_get_shader_info(self):
        """Test shader info extraction."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        shader_content = """/*{
    \"DESCRIPTION\": \"Test shader\",
    \"CREDIT\": \"Test\",
    \"CATEGORIES\": [\"Test\"],
    \"INPUTS\": []
}*/
void main() { gl_FragColor = vec4(1.0); }"""
        
        info = renderer.get_shader_info(shader_content)
        
        assert info["type"] == "ISF"
        assert info["size"] > 0
        assert info["lines"] > 0
        assert "name" in info
        assert "description" in info
    
    def test_create_placeholder_image(self):
        """Test placeholder image creation."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        shader_content = """/*{
    \"DESCRIPTION\": \"Test shader\",
    \"CREDIT\": \"Test\",
    \"CATEGORIES\": [\"Test\"],
    \"INPUTS\": []
}*/
void main() { gl_FragColor = vec4(1.0); }"""
        image = renderer._create_placeholder_image(shader_content, 1.0, 100, 100)
        
        assert isinstance(image, Image.Image)
        assert image.size == (100, 100)
        assert image.mode == 'RGB'
    
    def test_render_frame_creates_directory(self):
        """Test that render_frame creates output directory if needed."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        shader_content = """/*{
    \"DESCRIPTION\": \"Test shader\",
    \"CREDIT\": \"Test\",
    \"CATEGORIES\": [\"Test\"],
    \"INPUTS\": []
}*/
void main() { gl_FragColor = vec4(1.0); }"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "nested" / "output"
            output_path = output_dir / "test.png"
            
            renderer.render_frame(shader_content, 1.0, output_path)
            
            # Check that directory was created
            assert output_dir.exists()
            assert output_path.exists()
    
    def test_render_complex_eye_shader(self):
        """Test rendering a complex, known-good ISF shader (spherical eye)."""
        config = Config()
        renderer = ShaderRenderer(config)
        
        shader_content = """/*{
    \"CATEGORIES\": [],
    \"CREDIT\": \"Jim Cortez - Commune Project (Enhanced with Book of Shaders techniques)\",
    \"DESCRIPTION\": \"Creates an advanced spherical human eyeball with realistic eye anatomy and dynamic visual effects. Features eye movement speed and range, iris color controls, pupil and iris sizing, vein intensity, reflection intensity, texture detail controls, and LFO parameters for realistic eye animations.\",
    \"INPUTS\": [
        {\"NAME\": \"eyeMovementSpeed\", \"TYPE\": \"float\", \"LABEL\": \"Eye Movement Speed\", \"DEFAULT\": 0.8, \"MIN\": 0.0, \"MAX\": 3.0},
        {\"NAME\": \"eyeMovementRange\", \"TYPE\": \"float\", \"LABEL\": \"Eye Movement Range (Degrees)\", \"DEFAULT\": 12.0, \"MIN\": 0.0, \"MAX\": 30.0},
        {\"NAME\": \"irisHue\", \"TYPE\": \"float\", \"LABEL\": \"Iris Hue\", \"DEFAULT\": 0.6, \"MIN\": 0.0, \"MAX\": 1.0},
        {\"NAME\": \"irisSaturation\", \"TYPE\": \"float\", \"LABEL\": \"Iris Saturation\", \"DEFAULT\": 0.8, \"MIN\": 0.0, \"MAX\": 1.0},
        {\"NAME\": \"irisBrightness\", \"TYPE\": \"float\", \"LABEL\": \"Iris Brightness\", \"DEFAULT\": 0.7, \"MIN\": 0.0, \"MAX\": 1.0},
        {\"NAME\": \"scleraBrightness\", \"TYPE\": \"float\", \"LABEL\": \"Sclera Brightness\", \"DEFAULT\": 0.95, \"MIN\": 0.0, \"MAX\": 1.0},
        {\"NAME\": \"pupilSize\", \"TYPE\": \"float\", \"LABEL\": \"Pupil Size\", \"DEFAULT\": 0.12, \"MIN\": 0.05, \"MAX\": 0.3},
        {\"NAME\": \"irisSize\", \"TYPE\": \"float\", \"LABEL\": \"Iris Size\", \"DEFAULT\": 0.35, \"MIN\": 0.2, \"MAX\": 0.5},
        {\"NAME\": \"veinIntensity\", \"TYPE\": \"float\", \"LABEL\": \"Vein Intensity\", \"DEFAULT\": 0.4, \"MIN\": 0.0, \"MAX\": 1.0},
        {\"NAME\": \"reflectionIntensity\", \"TYPE\": \"float\", \"LABEL\": \"Reflection Intensity\", \"DEFAULT\": 0.9, \"MIN\": 0.0, \"MAX\": 1.0},
        {\"NAME\": \"textureDetail\", \"TYPE\": \"float\", \"LABEL\": \"Texture Detail\", \"DEFAULT\": 1.0, \"MIN\": 0.0, \"MAX\": 2.0},
        {\"NAME\": \"textureDetail2\", \"TYPE\": \"float\", \"LABEL\": \"Texture Detail 2\", \"DEFAULT\": 1.0, \"MIN\": 0.0, \"MAX\": 5.0},
        {\"NAME\": \"textureDetail3\", \"TYPE\": \"float\", \"LABEL\": \"Texture Detail 3\", \"DEFAULT\": 1.0, \"MIN\": 0.0, \"MAX\": 75.0},
        {\"NAME\": \"lfoRate\", \"TYPE\": \"float\", \"LABEL\": \"LFO Rate\", \"DEFAULT\": 4.0, \"MIN\": 0.0, \"MAX\": 10.0},
        {\"NAME\": \"lfoRateAmp\", \"TYPE\": \"float\", \"LABEL\": \"LFO Rate Amplitude\", \"DEFAULT\": 1.0, \"MIN\": 0.0, \"MAX\": 10.0}
    ],
    \"ISFVSN\": \"2\"
}*/

#define PI 3.14159265359
#define TWO_PI 6.28318530718

float hash(float n) { return fract(sin(n) * 43758.5453); }
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
float noise(vec2 p) { vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f); float a = hash(i); float b = hash(i + vec2(1.0, 0.0)); float c = hash(i + vec2(0.0, 1.0)); float d = hash(i + vec2(1.0, 1.0)); return mix(mix(a, b, f.x), mix(c, d, f.x), f.y); }
float fbm(vec2 p) { float f = 0.0; f += 0.50000 * textureDetail * noise(p); p = p * 2.02; f += 0.25000 * textureDetail2 * noise(p); p = p * 2.03; f += 0.12500 * noise(p); p = p * 2.01; f += 0.06250 * noise(p); p = p * 2.04; f += 0.03125 * noise(p); return f / 0.984375; }
float length2(vec2 p) { vec2 q = p * p * p * p; return pow(q.x + q.y, 1.0 / 4.0); }
vec3 hsb2rgb(vec3 c) { vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0); rgb = rgb * rgb * (3.0 - 2.0 * rgb); return c.z * mix(vec3(1.0), rgb, c.y); }
float smoothstep2(float edge0, float edge1, float x) { float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0); return t * t * (3.0 - 2.0 * t); }
mat3 rotateX(float angle) { float c = cos(angle); float s = sin(angle); return mat3(1.0, 0.0, 0.0, 0.0, c, -s, 0.0, s, c); }
mat3 rotateY(float angle) { float c = cos(angle); float s = sin(angle); return mat3(c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c); }
vec3 uvToSphere(vec2 uv) { float longitude = (uv.x - 0.5) * TWO_PI; float latitude = (uv.y - 0.5) * PI; float x = cos(latitude) * cos(longitude); float y = cos(latitude) * sin(longitude); float z = sin(latitude); return vec3(x, y, z); }
vec2 sphereToUV(vec3 sphere) { float longitude = atan(sphere.y, sphere.x); float latitude = asin(clamp(sphere.z, -1.0, 1.0)); float u = (longitude / TWO_PI) + 0.5; float v = (latitude / PI) + 0.5; return vec2(u, v); }
vec2 getEyeMovement(float time, float speed, float range) { float primaryX = sin(time * speed) * sin(time * speed * 0.3); float primaryY = cos(time * speed * 0.7) * sin(time * speed * 0.2); float tremorX = sin(time * speed * 8.0) * 0.1; float tremorY = cos(time * speed * 6.0) * 0.1; float driftX = sin(time * speed * 0.1) * 0.3; float driftY = cos(time * speed * 0.15) * 0.3; vec2 movement = vec2(primaryX + tremorX + driftX, primaryY + tremorY + driftY); return movement * range * PI / 180.0; }
void main() { vec2 uv = isf_FragNormCoord; vec3 spherePos = uvToSphere(uv); vec2 eyeMovement = getEyeMovement(TIME, eyeMovementSpeed, eyeMovementRange); mat3 rotationMatrix = rotateY(eyeMovement.x) * rotateX(eyeMovement.y); vec3 rotatedSphere = rotationMatrix * spherePos; vec2 eyeUV = sphereToUV(rotatedSphere); eyeUV = fract(eyeUV); vec2 center = vec2(0.5, 0.5); float dist = length(eyeUV - center); vec2 p = -1.0 + 2.0 * eyeUV; p.x *= RENDERSIZE.x / RENDERSIZE.y; float r = length(p); float a = atan(p.y, p.x); float dd = 0.2 * sin(lfoRate * TIME) * lfoRateAmp; float ss = 1.0 + clamp(1.0 - r, 0.0, 1.0) * dd; r *= ss; vec3 col = vec3(0.0, 0.3, 0.4); float f = fbm(5.0 * p); col = mix(col, vec3(0.2, 0.5, 0.4), f); col = mix(col, vec3(0.9, 0.6, 0.2), 1.0 - smoothstep(0.2, 0.6, r)); a += textureDetail3 * fbm(20.0 * p); f = smoothstep(0.3, 1.0, fbm(vec2(20.0 * a, 6.0 * r))); col = mix(col, vec3(1.0, 1.0, 1.0), f); vec3 irisColor = hsb2rgb(vec3(irisHue, irisSaturation, irisBrightness)); float irisMask = smoothstep2(irisSize, irisSize - 0.05, dist); col = mix(col, irisColor, irisMask * 0.8); f = smoothstep(0.4, 0.9, fbm(vec2(15.0 * a, 10.0 * r))); col *= 1.0 - 0.5 * f; col *= 1.0 - 0.25 * smoothstep(0.6, 0.8, r); float pupilMask = smoothstep2(pupilSize, pupilSize - 0.02, dist); vec3 pupilColor = vec3(0.0, 0.0, 0.0); float pupilDepth = smoothstep2(0.0, pupilSize * 0.5, dist); pupilColor += pupilDepth * 0.1; col = mix(col, pupilColor, pupilMask); f = 1.0 - smoothstep(0.0, 0.6, length2(mat2(0.6, 0.8, -0.8, 0.6) * (p - vec2(0.3, 0.5)) * vec2(1.0, 2.0))); col += vec3(1.0, 0.9, 0.9) * f * 0.985 * reflectionIntensity; col *= vec3(0.8 + 0.2 * cos(r * a)); f = 1.0 - smoothstep(0.2, 0.25, r); col = mix(col, vec3(0.0), f); f = smoothstep(0.79, 0.82, r); col = mix(col, vec3(1.0), f); col *= 0.5 + 0.5 * pow(16.0 * eyeUV.x * eyeUV.y * (1.0 - eyeUV.x) * (1.0 - eyeUV.y), 0.1); float veins = fbm(eyeUV * 8.0 + TIME * 0.1) * veinIntensity; veins *= smoothstep2(0.0, 0.4, dist) * smoothstep2(0.5, 0.4, dist); veins *= smoothstep2(0.0, 0.1, veins); col += veins * vec3(0.8, 0.2, 0.2) * 0.15; float chromaOffset = 0.002; vec2 chromaUV = eyeUV + vec2(chromaOffset, 0.0); float chromaDist = length(chromaUV - center); float chromaMask = smoothstep2(irisSize, irisSize - 0.05, chromaDist); col.r += chromaMask * 0.1; float ao = smoothstep2(0.0, 0.2, dist) * 0.4; col *= 1.0 - ao; float scleraMask = smoothstep2(0.45, 0.5, dist); vec3 scleraColor = vec3(scleraBrightness) + vec3(0.02, 0.01, 0.01); col = mix(col, scleraColor, scleraMask * 0.3); gl_FragColor = vec4(col, 1.0); }"""
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = Path(f.name)
        try:
            renderer.render_frame(shader_content, 0.0, output_path)
            assert output_path.exists()
            image = Image.open(output_path)
            assert image.size == (1920, 1080)  # Default size
            assert image.mode == 'RGBA'
        finally:
            output_path.unlink() 