#!/usr/bin/env python3
"""
Framework-specific reproduction script for pyvvisf bugs.
This script mimics the exact usage pattern from the isf-shader-renderer framework.
"""

import sys
import time
import tempfile
from pathlib import Path

def test_framework_usage_pattern():
    """Test the exact usage pattern from the framework"""
    print("=== Framework Usage Pattern Test ===")
    try:
        import pyvvisf

        # Step 1: Initialize buffer pool (like the framework does)
        buffer_pool = None
        try:
            buffer_pool = pyvvisf.GLBufferPool()
            print("✓ GLBufferPool initialized")
        except Exception as e:
            print(f"✗ GLBufferPool initialization failed: {e}")

        # Step 2: Create scene and load shader (like framework)
        shader_content = '''/*{
    "DESCRIPTION": "Framework test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0);
}'''

        scene = pyvvisf.CreateISFSceneRef()
        doc = pyvvisf.CreateISFDocRefWith(shader_content)
        scene.use_doc(doc)
        print("✓ Scene and shader loaded")

        # Step 3: Multiple renders with cleanup (like framework)
        for i in range(3):
            print(f"  Rendering frame {i}...")

            # Clean up buffer pool before each render (like framework)
            if buffer_pool is not None:
                try:
                    buffer_pool.cleanup()
                    print(f"    ✓ Buffer pool cleaned up before frame {i}")
                except Exception as cleanup_exc:
                    print(f"    ⚠ Buffer pool cleanup failed: {cleanup_exc}")

            # Force reinitialize OpenGL context (like framework)
            try:
                pyvvisf.reinitialize_glfw_context()
                gl_info = pyvvisf.get_gl_info()
                print(f"    ✓ OpenGL context reinitialized for frame {i}")
            except Exception as ctx_exc:
                print(f"    ⚠ OpenGL context reinitialization failed: {ctx_exc}")

            # Set inputs
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(float(i)), "TIME")
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.x")
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.y")

            # Create buffer and render
            size = pyvvisf.Size(64, 64)
            buffer = scene.create_and_render_a_buffer(size)

            print(f"    ✓ Frame {i} buffer created: {buffer}")

            # Convert to PIL (like framework)
            try:
                if hasattr(buffer, 'to_pil_image'):
                    image = buffer.to_pil_image()
                    print(f"    ✓ Frame {i} PIL image: {image.size}")
                else:
                    print(f"    ⚠ Frame {i} no to_pil_image method")
            except Exception as pil_exc:
                print(f"    ⚠ Frame {i} PIL conversion failed: {pil_exc}")

        # Step 4: Cleanup (like framework)
        print("  Cleaning up...")

        # Scene cleanup
        if scene:
            try:
                scene.prepare_to_be_deleted()
                print("    ✓ Scene prepared for deletion")
            except Exception as e:
                print(f"    ⚠ Scene cleanup failed: {e}")

        # Buffer pool cleanup
        if buffer_pool is not None:
            try:
                if hasattr(buffer_pool, 'cleanup'):
                    buffer_pool.cleanup()
                if hasattr(buffer_pool, 'housekeeping'):
                    buffer_pool.housekeeping()
                if hasattr(buffer_pool, 'purge'):
                    buffer_pool.purge()
                print("    ✓ Buffer pool cleaned up")
            except Exception as e:
                print(f"    ⚠ Buffer pool cleanup failed: {e}")

        print("✓ Framework usage pattern completed successfully")
        return True

    except Exception as e:
        print(f"✗ Framework usage pattern failed: {e}")
        return False

def test_stress_rendering():
    """Test stress rendering like the framework's stress test"""
    print("\n=== Stress Rendering Test ===")
    try:
        import pyvvisf

        # Create multiple renderers (like framework might do)
        renderers = []
        for i in range(3):
            try:
                # Initialize buffer pool
                buffer_pool = pyvvisf.GLBufferPool()

                # Create scene
                scene = pyvvisf.CreateISFSceneRef()

                # Load shader
                shader_content = f'''/*{{
    "DESCRIPTION": "Stress test shader {i}",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}}*/
void main() {{
    gl_FragColor = vec4({i * 0.1}, 0.5, 0.5, 1.0);
}}'''

                doc = pyvvisf.CreateISFDocRefWith(shader_content)
                scene.use_doc(doc)

                renderers.append({
                    'buffer_pool': buffer_pool,
                    'scene': scene,
                    'index': i
                })
                print(f"  ✓ Renderer {i} created")
            except Exception as e:
                print(f"  ✗ Renderer {i} creation failed: {e}")

        # Render with each renderer
        for renderer in renderers:
            try:
                print(f"  Rendering with renderer {renderer['index']}...")

                # Cleanup before render
                if renderer['buffer_pool']:
                    renderer['buffer_pool'].cleanup()

                # Reinitialize context
                pyvvisf.reinitialize_glfw_context()

                # Set inputs
                scene = renderer['scene']
                scene.set_value_for_input_named(pyvvisf.ISFFloatVal(0.0), "TIME")
                scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.x")
                scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.y")

                # Render
                size = pyvvisf.Size(64, 64)
                buffer = scene.create_and_render_a_buffer(size)

                print(f"    ✓ Renderer {renderer['index']} buffer: {buffer}")

            except Exception as e:
                print(f"    ✗ Renderer {renderer['index']} rendering failed: {e}")

        # Cleanup all renderers
        for renderer in renderers:
            try:
                if renderer['scene']:
                    renderer['scene'].prepare_to_be_deleted()
                if renderer['buffer_pool']:
                    renderer['buffer_pool'].cleanup()
                print(f"  ✓ Renderer {renderer['index']} cleaned up")
            except Exception as e:
                print(f"  ⚠ Renderer {renderer['index']} cleanup failed: {e}")

        print("✓ Stress rendering completed")
        return True

    except Exception as e:
        print(f"✗ Stress rendering failed: {e}")
        return False

def test_context_cleanup_issues():
    """Test context cleanup issues"""
    print("\n=== Context Cleanup Issues Test ===")
    try:
        import pyvvisf

        # Test multiple context reinitializations
        for i in range(5):
            print(f"  Context reinitialization {i}...")
            try:
                pyvvisf.reinitialize_glfw_context()
                gl_info = pyvvisf.get_gl_info()
                print(f"    ✓ Context {i} valid: {gl_info['context_valid']}")
            except Exception as e:
                print(f"    ✗ Context {i} failed: {e}")

        # Test creating objects after context reinitialization
        try:
            scene = pyvvisf.CreateISFSceneRef()
            print("  ✓ Scene created after context reinitialization")

            shader_content = '''/*{
    "DESCRIPTION": "Test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}'''

            doc = pyvvisf.CreateISFDocRefWith(shader_content)
            scene.use_doc(doc)
            print("  ✓ Shader loaded after context reinitialization")

            # Try to render
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(0.0), "TIME")
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.x")
            scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.y")

            size = pyvvisf.Size(64, 64)
            buffer = scene.create_and_render_a_buffer(size)
            print("  ✓ Render successful after context reinitialization")

        except Exception as e:
            print(f"  ✗ Post-reinitialization operations failed: {e}")

        print("✓ Context cleanup issues test completed")
        return True

    except Exception as e:
        print(f"✗ Context cleanup issues test failed: {e}")
        return False

def main():
    """Run all framework-specific tests"""
    print("pyvvisf Framework Bug Reproduction Script")
    print("=" * 60)

    tests = [
        test_framework_usage_pattern,
        test_stress_rendering,
        test_context_cleanup_issues,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed < total:
        print("❌ Some tests failed - framework-specific bugs detected!")
        return 1
    else:
        print("✅ All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
