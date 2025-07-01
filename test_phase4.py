#!/usr/bin/env python3
"""Test script for Phase 4: ISF Shader Rendering Implementation."""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from isf_shader_renderer.renderer import ShaderRenderer
from isf_shader_renderer.config import Config, Defaults

def test_phase4():
    """Test Phase 4 implementation."""
    print("Testing Phase 4: ISF Shader Rendering Implementation")
    print("=" * 60)
    
    # Create a simple ISF shader
    shader_content = """
/*{
    "DESCRIPTION": "A simple test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": [
        {
            "NAME": "color",
            "TYPE": "color",
            "DEFAULT": [1.0, 0.0, 0.0, 1.0]
        },
        {
            "NAME": "speed",
            "TYPE": "float",
            "DEFAULT": 1.0,
            "MIN": 0.0,
            "MAX": 10.0
        }
    ]
}*/

void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(uv, center);
    float wave = sin(dist * 20.0 + TIME * speed) * 0.5 + 0.5;
    gl_FragColor = vec4(color.rgb * wave, color.a);
}
"""
    
    # Create configuration
    config = Config()
    config.defaults = Defaults(width=640, height=480, quality=95)
    
    # Create renderer
    renderer = ShaderRenderer(config)
    
    print("1. Testing shader validation...")
    is_valid = renderer.validate_shader(shader_content)
    print(f"   Shader validation: {'PASS' if is_valid else 'FAIL'}")
    
    print("\n2. Testing shader info extraction...")
    info = renderer.get_shader_info(shader_content)
    print(f"   Shader name: {info.get('name', 'Unknown')}")
    print(f"   VVISF available: {info.get('vvisf_available', False)}")
    print(f"   Inputs: {len(info.get('inputs', []))}")
    
    print("\n3. Testing frame rendering...")
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Test rendering at different times
    times = [0.0, 1.0, 2.0, 3.0]
    for i, time_code in enumerate(times):
        output_path = output_dir / f"phase4_test_{i:02d}.png"
        try:
            renderer.render_frame(
                shader_content=shader_content,
                time_code=time_code,
                output_path=output_path
            )
            print(f"   Rendered frame {i+1}/{len(times)} at time {time_code}s -> {output_path}")
        except Exception as e:
            print(f"   Failed to render frame {i+1}: {e}")
    
    print("\n4. Testing with shader inputs...")
    # Create a shader config with inputs
    from isf_shader_renderer.config import ShaderConfig
    shader_config = ShaderConfig(
        input="test.fs",
        output="test_output/with_inputs_%04d.png",
        times=[0.0],
        width=320,
        height=240,
        inputs={
            "color": [0.0, 1.0, 0.0, 1.0],  # Green
            "speed": 2.0
        }
    )
    
    try:
        output_path = output_dir / "phase4_with_inputs.png"
        renderer.render_frame(
            shader_content=shader_content,
            time_code=1.5,
            output_path=output_path,
            shader_config=shader_config
        )
        print(f"   Rendered frame with custom inputs -> {output_path}")
    except Exception as e:
        print(f"   Failed to render with inputs: {e}")
    
    print("\n5. Testing cleanup...")
    renderer.cleanup()
    print("   Cleanup completed")
    
    print("\nPhase 4 test completed!")
    print(f"Check output files in: {output_dir.absolute()}")

if __name__ == "__main__":
    test_phase4() 