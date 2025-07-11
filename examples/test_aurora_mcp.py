#!/usr/bin/env python3
"""Example script demonstrating Aurora shader usage through MCP framework."""

import asyncio
import json
import base64
from pathlib import Path

# Aurora Borealis shader content
AURORA_SHADER = """/*{
    "CATEGORIES": ["Nature", "Aurora", "Organic", "Flow"],
    "CREDIT": "Jim Cortez - Commune Project (Original: ISF Import by Old Salt)",
    "DESCRIPTION": "Creates a mesmerizing aurora borealis effect with flowing, ethereal light patterns that dance across the screen. Features multiple layers of sinuous light bands that move and morph organically, simulating the natural phenomenon of the northern lights with customizable colors and movement controls.",
    "INPUTS": [
        {
            "DEFAULT": [0.0, 1.0, 0.0, 1.0],
            "NAME": "uC1",
            "TYPE": "color"
        },
        {
            "DEFAULT": [0.0, 0.0, 1.0, 1.0],
            "NAME": "uC2",
            "TYPE": "color"
        },
        {
            "DEFAULT": [1.0, 0.0, 0.0, 1.0],
            "NAME": "uC3",
            "TYPE": "color"
        },
        {
            "DEFAULT": [0.0, 0.0],
            "LABEL": "Offset: ",
            "MAX": [1.0, 1.0],
            "MIN": [-1.0, -1.0],
            "NAME": "uOffset",
            "TYPE": "point2D"
        },
        {
            "DEFAULT": 1.0,
            "LABEL": "Zoom: ",
            "MAX": 10.0,
            "MIN": 1.0,
            "NAME": "uZoom",
            "TYPE": "float"
        },
        {
            "DEFAULT": 0.0,
            "LABEL": "Rotation(or R Speed):",
            "MAX": 180.0,
            "MIN": -180.0,
            "NAME": "uRotate",
            "TYPE": "float"
        },
        {
            "DEFAULT": 1,
            "LABEL": "Continuous Rotation? ",
            "NAME": "uContRot",
            "TYPE": "bool"
        },
        {
            "DEFAULT": 0,
            "LABEL": "Color Mode: ",
            "LABELS": [
                "Shader Defaults ",
                "Alternate Color Palette (3 used) "
            ],
            "NAME": "uColMode",
            "TYPE": "long",
            "VALUES": [0, 1]
        },
        {
            "DEFAULT": 1.0,
            "LABEL": "Intensity: ",
            "MAX": 4.0,
            "MIN": 0.0,
            "NAME": "uIntensity",
            "TYPE": "float"
        },
        {
            "DEFAULT": 18.0,
            "LABEL": "Iterations: ",
            "MAX": 32.0,
            "MIN": 8.0,
            "NAME": "uIterations",
            "TYPE": "float"
        },
        {
            "DEFAULT": 0.3,
            "LABEL": "Animation Speed: ",
            "MAX": 2.0,
            "MIN": 0.0,
            "NAME": "uAnimSpeed",
            "TYPE": "float"
        },
        {
            "DEFAULT": 0.99,
            "LABEL": "Scale Factor: ",
            "MAX": 1.0,
            "MIN": 0.8,
            "NAME": "uScaleFactor",
            "TYPE": "float"
        }
    ],
    "ISFVSN": "2"
}*/

/*
ORIGINAL SHADER INFORMATION:
- Original Author: ISF Import by Old Salt
- Original Shader: http://www.glslsandbox.com/e#58544.0
- Source: Originally sourced from editor.isf.video - Aurora by ISF Import by Old Salt
- Description: Aurora borealis effect with flowing, ethereal light patterns
- License: GLSL Sandbox license
- Features: Color customization, rotation controls, zoom and offset functions
*/

#define PI 3.141592653589
#define rotate2D(a) mat2(cos(a),-sin(a),sin(a),cos(a))

void main()
{
    vec2 uv = gl_FragCoord.xy/RENDERSIZE - 0.5; // normalize coordinates
    uv.x *= RENDERSIZE.x/RENDERSIZE.y;          // correct aspect ratio
    uv = (uv-uOffset) * 3.0/uZoom;              // offset and zoom functions
    
    // Fixed rotation calculation - now consistent between continuous and static modes
    float rotationAngle = uRotate * PI / 180.0;
    if (uContRot) {
        rotationAngle += TIME * uAnimSpeed;
    }
    uv = uv * rotate2D(rotationAngle);

    vec2 p = uv;
    float d = 2.0 * length(p);
    vec3 col = vec3(0.0); 
    
    // Use configurable iterations with proper casting and GLSL-compatible loop
    int iterations = int(clamp(uIterations, 8.0, 32.0));
    
    // GLSL-compatible loop with fixed bounds and blend factor for fractional iterations
    for (int i = 0; i < 32; i++)
    {
        float blendFactor = 1.0;
        if (float(i) >= float(iterations)) {
            blendFactor = 0.0;
        }
        
        float dist = abs(p.y + sin(float(i) + TIME * uAnimSpeed + 3.0 * p.x)) - 0.2;
        if (dist < 1.0) { 
            col += blendFactor * (1.0 - pow(abs(dist), 0.28)) * vec3(0.8 + 0.2 * sin(TIME), 0.9 + 0.1 * sin(TIME * 1.1), 1.2); 
        }
        
        // Improved precision with safer division
        float scaleDivisor = max(d, 1e-6);
        p *= uScaleFactor / scaleDivisor; 
        p *= rotate2D(PI / 60.0);
    }
    col *= 0.49; 

    vec4 cShad = vec4(col - d - 0.4, 1.0);  
    vec3 cOut = cShad.rgb;
    
    // Optimized color mode switching
    if (uColMode == 1) {
        cOut = uC1.rgb * cShad.r + uC2.rgb * cShad.g + uC3.rgb * cShad.b;
    }
    
    cOut = cOut * uIntensity;
    cOut = clamp(cOut, vec3(0.0), vec3(1.0));
    gl_FragColor = vec4(cOut.rgb, cShad.a);
}"""


async def test_aurora_shader_mcp():
    """Test the Aurora shader through MCP framework."""
    from isf_shader_renderer.mcp.handlers import ISFShaderHandlers
    
    print("Testing Aurora Borealis Shader through MCP Framework")
    print("=" * 60)
    
    # Create handlers
    handlers = ISFShaderHandlers()
    
    # Test 1: Validate Aurora shader
    print("\n1. Testing Aurora shader validation...")
    result = await handlers.call_tool("validate_shader", {
        "shader_content": AURORA_SHADER
    })
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result.get('errors'):
        print(f"Errors: {result['errors']}")
    if result.get('warnings'):
        print(f"Warnings: {result['warnings']}")
    
    # Test 2: Get Aurora shader info
    print("\n2. Testing Aurora shader info extraction...")
    result = await handlers.call_tool("get_shader_info", {
        "shader_content": AURORA_SHADER
    })
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result.get('shader_info'):
        info = result['shader_info']
        print(f"Aurora Shader Info:")
        print(f"  Type: {info.get('type')}")
        print(f"  Size: {info.get('size')} characters")
        print(f"  Lines: {info.get('lines')}")
        print(f"  Has TIME uniform: {info.get('has_time_uniform')}")
        print(f"  Has RENDERSIZE uniform: {info.get('has_resolution_uniform')}")
        print(f"  Description: {info.get('description', 'N/A')}")
        print(f"  Credit: {info.get('credit', 'N/A')}")
        print(f"  Categories: {info.get('categories', [])}")
        print(f"  Input Count: {info.get('input_count', 0)}")
    
    # Test 3: Render Aurora shader with default settings
    print("\n3. Testing Aurora shader rendering (default settings)...")
    result = await handlers.call_tool("render_shader", {
        "shader_content": AURORA_SHADER,
        "time_codes": [0.0, 1.0, 2.0],
        "width": 640,
        "height": 480,
        "quality": 95,
        "verbose": True
    })
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Rendered frames: {len(result['rendered_frames'])}")
    if result.get('metadata'):
        metadata = result['metadata']
        print(f"Metadata: {metadata}")
    
    # Test 4: Render Aurora shader with custom parameters
    print("\n4. Testing Aurora shader rendering (custom parameters)...")
    result = await handlers.call_tool("render_shader", {
        "shader_content": AURORA_SHADER,
        "time_codes": [0.5],
        "width": 800,
        "height": 600,
        "quality": 90,
        "verbose": False,
        "shader_inputs": {
            "uColMode": 1,  # Use alternate color palette
            "uIntensity": 2.0,  # Higher intensity
            "uZoom": 1.5,  # Zoom in
            "uAnimSpeed": 0.5,  # Faster animation
            "uContRot": True,  # Enable continuous rotation
            "uC1": [1.0, 0.0, 0.0, 1.0],  # Red
            "uC2": [0.0, 1.0, 0.0, 1.0],  # Green
            "uC3": [0.0, 0.0, 1.0, 1.0],  # Blue
        }
    })
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Rendered frames: {len(result['rendered_frames'])}")
    
    # Test 5: Create animation sequence
    print("\n5. Testing Aurora shader animation sequence...")
    time_codes = [i * 0.2 for i in range(15)]  # 0.0, 0.2, 0.4, ..., 2.8
    
    result = await handlers.call_tool("render_shader", {
        "shader_content": AURORA_SHADER,
        "time_codes": time_codes,
        "width": 480,
        "height": 360,
        "quality": 85,
        "verbose": True,
        "shader_inputs": {
            "uContRot": True,  # Enable continuous rotation
            "uAnimSpeed": 0.8,  # Medium animation speed
            "uIterations": 24.0,  # More iterations for detail
            "uIntensity": 1.5,  # Medium intensity
        }
    })
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Rendered frames: {len(result['rendered_frames'])}")
    if result.get('metadata'):
        metadata = result['metadata']
        print(f"Animation metadata: {metadata}")
    
    # Save example frames
    print("\n6. Saving example frames...")
    if result['rendered_frames']:
        # Save first frame as example
        import base64
        from PIL import Image
        import io
        
        # Create output directory
        output_dir = Path("examples/aurora_output")
        output_dir.mkdir(exist_ok=True)
        
        # Save first frame
        image_data = base64.b64decode(result['rendered_frames'][0])
        image = Image.open(io.BytesIO(image_data))
        output_path = output_dir / "aurora_frame_0.jpg"
        image.save(output_path)
        print(f"Saved first frame to: {output_path}")
        
        # Save middle frame
        if len(result['rendered_frames']) > 7:
            image_data = base64.b64decode(result['rendered_frames'][7])
            image = Image.open(io.BytesIO(image_data))
            output_path = output_dir / "aurora_frame_7.jpg"
            image.save(output_path)
            print(f"Saved middle frame to: {output_path}")
        
        # Save last frame
        image_data = base64.b64decode(result['rendered_frames'][-1])
        image = Image.open(io.BytesIO(image_data))
        output_path = output_dir / "aurora_frame_last.jpg"
        image.save(output_path)
        print(f"Saved last frame to: {output_path}")
    
    print("\nAurora shader MCP test completed!")


def main():
    """Main function."""
    print("Aurora Borealis Shader MCP Example")
    print("This example demonstrates the Aurora shader through the MCP framework.")
    print("The shader creates mesmerizing aurora borealis effects with customizable parameters.")
    print()
    
    try:
        asyncio.run(test_aurora_shader_mcp())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 