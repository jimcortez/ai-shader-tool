#!/usr/bin/env python3
"""
Minimal reproduction script for pyvvisf bugs.
This script demonstrates the segmentation faults and other issues found in pyvvisf.
"""

import sys
import tempfile
from pathlib import Path

def test_basic_pyvvisf_import():
    """Test 1: Basic import and initialization"""
    print("=== Test 1: Basic import and initialization ===")
    try:
        import pyvvisf
        print(f"✓ pyvvisf imported successfully, version: {getattr(pyvvisf, '__version__', 'unknown')}")

        # Check available functions
        print(f"✓ Available functions: {[f for f in dir(pyvvisf) if not f.startswith('_')]}")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_simple_shader_creation():
    """Test 2: Simple shader creation"""
    print("\n=== Test 2: Simple shader creation ===")
    try:
        import pyvvisf

        # Simple shader content
        shader_content = '''/*{
    "DESCRIPTION": "Simple test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}'''

        # Create ISFDoc
        doc = pyvvisf.CreateISFDocRefWith(shader_content)
        print(f"✓ ISFDoc created: {doc}")
        print(f"✓ Shader name: {doc.name}")
        print(f"✓ Shader description: {doc.description}")
        return True
    except Exception as e:
        print(f"✗ Shader creation failed: {e}")
        return False

def test_scene_creation():
    """Test 3: Scene creation"""
    print("\n=== Test 3: Scene creation ===")
    try:
        import pyvvisf

        # Create scene
        scene = pyvvisf.CreateISFSceneRef()
        print(f"✓ Scene created: {scene}")
        return True
    except Exception as e:
        print(f"✗ Scene creation failed: {e}")
        return False

def test_simple_rendering():
    """Test 4: Simple rendering (this may segfault)"""
    print("\n=== Test 4: Simple rendering ===")
    try:
        import pyvvisf

        # Simple shader
        shader_content = '''/*{
    "DESCRIPTION": "Simple test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}'''

        # Create scene and load shader
        scene = pyvvisf.CreateISFSceneRef()
        doc = pyvvisf.CreateISFDocRefWith(shader_content)
        scene.use_doc(doc)

        # Set time
        scene.set_value_for_input_named(pyvvisf.ISFFloatVal(0.0), "TIME")

        # Set resolution
        scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.x")
        scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.y")

        # Create buffer and render
        size = pyvvisf.Size(64, 64)
        buffer = scene.create_and_render_a_buffer(size)

        print(f"✓ Buffer created: {buffer}")
        print(f"✓ Buffer name: {getattr(buffer, 'name', 'N/A')}")
        print(f"✓ Buffer size: {getattr(buffer, 'size', 'N/A')}")

        return True
    except Exception as e:
        print(f"✗ Simple rendering failed: {e}")
        return False

def test_multiple_renders():
    """Test 5: Multiple renders (this may segfault)"""
    print("\n=== Test 5: Multiple renders ===")
    try:
        import pyvvisf

        # Simple shader
        shader_content = '''/*{
    "DESCRIPTION": "Simple test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}'''

        # Create scene and load shader
        scene = pyvvisf.CreateISFSceneRef()
        doc = pyvvisf.CreateISFDocRefWith(shader_content)
        scene.use_doc(doc)

        # Multiple renders
        for i in range(3):
            print(f"  Rendering frame {i}...")

            # Set time
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(float(i)), "TIME")

            # Set resolution
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.x")
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.y")

            # Create buffer and render
            size = pyvvisf.Size(64, 64)
            buffer = scene.create_and_render_a_buffer(size)

            print(f"    ✓ Frame {i} buffer: {buffer}")

        print("✓ Multiple renders completed successfully")
        return True
    except Exception as e:
        print(f"✗ Multiple renders failed: {e}")
        return False

def test_buffer_to_pil():
    """Test 6: Buffer to PIL conversion"""
    print("\n=== Test 6: Buffer to PIL conversion ===")
    try:
        import pyvvisf
        from PIL import Image

        # Simple shader
        shader_content = '''/*{
    "DESCRIPTION": "Simple test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}'''

        # Create scene and load shader
        scene = pyvvisf.CreateISFSceneRef()
        doc = pyvvisf.CreateISFDocRefWith(shader_content)
        scene.use_doc(doc)

        # Set inputs
        scene.set_value_for_input_named(pyvvisf.ISFFloatVal(0.0), "TIME")
        scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.x")
        scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.y")

        # Create buffer and render
        size = pyvvisf.Size(64, 64)
        buffer = scene.create_and_render_a_buffer(size)

        # Convert to PIL
        if hasattr(buffer, 'to_pil_image'):
            image = buffer.to_pil_image()
            print(f"✓ PIL image created: {image.size}, {image.mode}")
        else:
            print("✗ Buffer does not have to_pil_image method")
            return False

        return True
    except Exception as e:
        print(f"✗ Buffer to PIL conversion failed: {e}")
        return False

def test_glfw_context_management():
    """Test 7: GLFW context management"""
    print("\n=== Test 7: GLFW context management ===")
    try:
        import pyvvisf

        # Check available context functions
        context_funcs = [f for f in dir(pyvvisf) if 'context' in f.lower() or 'glfw' in f.lower()]
        print(f"✓ Available context functions: {context_funcs}")

        # Test reinitializing context
        if hasattr(pyvvisf, 'reinitialize_glfw_context'):
            pyvvisf.reinitialize_glfw_context()
            print("✓ Context reinitialized")

        # Test getting GL info
        if hasattr(pyvvisf, 'get_gl_info'):
            gl_info = pyvvisf.get_gl_info()
            print(f"✓ GL info: {gl_info}")

        return True
    except Exception as e:
        print(f"✗ Context management failed: {e}")
        return False

def main():
    """Run all tests"""
    print("pyvvisf Bug Reproduction Script")
    print("=" * 50)

    tests = [
        test_basic_pyvvisf_import,
        test_simple_shader_creation,
        test_scene_creation,
        test_simple_rendering,
        test_multiple_renders,
        test_buffer_to_pil,
        test_glfw_context_management,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed < total:
        print("❌ Some tests failed - bugs detected!")
        return 1
    else:
        print("✅ All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
