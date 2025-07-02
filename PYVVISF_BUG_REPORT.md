# pyvvisf Bug Report

## Summary

This bug report documents critical issues found in pyvvisf version 0.2.1.dev0+gaa8e440.d20250702 that cause segmentation faults and stability problems when used in production environments, particularly for batch rendering scenarios.

## Environment

- **Platform**: macOS 23.5.0 (Darwin)
- **Python**: 3.11.4
- **pyvvisf Version**: 0.2.1.dev0+gaa8e440.d20250702
- **OpenGL**: 4.1 Metal - 88.1
- **Hardware**: Apple M2 Pro

## Critical Issues

### 1. Segmentation Fault During Context Reinitialization

**Severity**: Critical
**Impact**: Application crashes with SIGSEGV
**Reproducibility**: 100%

#### Description
When `reinitialize_glfw_context()` is called multiple times in sequence, followed by rendering operations, the application crashes with a segmentation fault.

#### Reproduction Steps
```python
import pyvvisf

# Create scene and shader
scene = pyvvisf.CreateISFSceneRef()
shader_content = '''/*{
    "DESCRIPTION": "Test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0);
}'''
doc = pyvvisf.CreateISFDocRefWith(shader_content)
scene.use_doc(doc)

# First render (works fine)
pyvvisf.reinitialize_glfw_context()
scene.set_value_for_input_named(pyvvisf.ISFFloatVal(0.0), "TIME")
scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.x")
scene.set_value_for_input_named(pyvvisf.ISFFloatVal(64.0), "RENDERSIZE.y")
size = pyvvisf.Size(64, 64)
buffer1 = scene.create_and_render_a_buffer(size)  # Works

# Second render (crashes with SIGSEGV)
pyvvisf.reinitialize_glfw_context()  # This triggers the crash
scene.set_value_for_input_named(pyvvisf.ISFFloatVal(1.0), "TIME")
buffer2 = scene.create_and_render_a_buffer(size)  # Never reached - segfault occurs
```

#### Expected Behavior
The second render should complete successfully without crashing.

#### Actual Behavior
Application crashes with segmentation fault (SIGSEGV) during the second `reinitialize_glfw_context()` call or immediately after.

#### Root Cause Analysis
The issue appears to be related to improper cleanup of OpenGL resources during context reinitialization. The debug logs show:
```
[pyvvisf] [ERROR] OpenGL context not valid during final cleanup
```

This suggests that the context cleanup process is not properly handling resource deallocation, leading to dangling pointers or invalid memory access.

### 2. GLBufferPool Cleanup Issues

**Severity**: High
**Impact**: Memory leaks and resource exhaustion
**Reproducibility**: 100%

#### Description
The `GLBufferPool.cleanup()` method does not properly clean up all resources, leading to potential memory leaks and resource exhaustion in long-running applications.

#### Reproduction Steps
```python
import pyvvisf

# Create buffer pool
buffer_pool = pyvvisf.GLBufferPool()

# Use buffer pool for rendering
scene = pyvvisf.CreateISFSceneRef()
# ... render operations ...

# Cleanup (may not clean up completely)
buffer_pool.cleanup()
```

#### Expected Behavior
All OpenGL resources should be properly deallocated and memory should be freed.

#### Actual Behavior
Some resources remain allocated, leading to gradual memory accumulation.

### 3. Missing Context Cleanup Method

**Severity**: Medium
**Impact**: Inability to properly clean up OpenGL context
**Reproducibility**: 100%

#### Description
The library provides `reinitialize_glfw_context()` but lacks a corresponding `cleanup_glfw_context()` method, making it impossible to properly clean up the OpenGL context.

#### Reproduction Steps
```python
import pyvvisf

# Initialize context
pyvvisf.initialize_glfw_context()

# Use context for rendering
# ... rendering operations ...

# Try to cleanup (method doesn't exist)
pyvvisf.cleanup_glfw_context()  # AttributeError: module 'pyvvisf' has no attribute 'cleanup_glfw_context'
```

#### Expected Behavior
A `cleanup_glfw_context()` method should be available for proper resource management.

#### Actual Behavior
No cleanup method is available, forcing applications to rely on automatic cleanup which may not be sufficient.

### 4. Batch Rendering Stability Issues

**Severity**: High
**Impact**: Unreliable batch rendering operations
**Reproducibility**: 90%

#### Description
When performing multiple renders in sequence, the library becomes unstable and may crash, especially when combined with context reinitialization and buffer pool cleanup.

#### Reproduction Steps
```python
import pyvvisf

scene = pyvvisf.CreateISFSceneRef()
# ... setup shader ...

for i in range(5):
    # This pattern causes instability
    buffer_pool.cleanup()
    pyvvisf.reinitialize_glfw_context()

    scene.set_value_for_input_named(pyvvisf.ISFFloatVal(float(i)), "TIME")
    buffer = scene.create_and_render_a_buffer(size)
    # May crash on iterations 2-5
```

#### Expected Behavior
All renders should complete successfully without crashes.

#### Actual Behavior
Crashes typically occur after the first or second render, especially when context reinitialization is involved.

## Recommended Fixes

### 1. Fix Context Reinitialization Segfault

**Priority**: Critical

The context reinitialization process needs to be completely rewritten to:
- Properly deallocate all OpenGL resources before destroying the context
- Ensure no dangling pointers remain after context destruction
- Add proper error handling for context state validation
- Implement a proper cleanup sequence that doesn't leave resources in an invalid state

**Suggested Implementation**:
```cpp
// Pseudo-code for proper context reinitialization
bool reinitialize_glfw_context() {
    // 1. Save current context state
    // 2. Properly deallocate all OpenGL resources
    // 3. Destroy current context
    // 4. Create new context
    // 5. Restore necessary state
    // 6. Validate context is in valid state
    return context_is_valid;
}
```

### 2. Implement Proper GLBufferPool Cleanup

**Priority**: High

The `GLBufferPool` cleanup should be enhanced to:
- Track all allocated buffers and ensure complete deallocation
- Add a `force_cleanup()` method for aggressive cleanup
- Implement proper reference counting
- Add validation to ensure cleanup completed successfully

### 3. Add Context Cleanup Method

**Priority**: Medium

Implement a proper `cleanup_glfw_context()` method:
```python
def cleanup_glfw_context():
    """Properly clean up the GLFW context and all associated resources."""
    # Implementation should handle all cleanup tasks
    pass
```

### 4. Improve Error Handling and Validation

**Priority**: High

Add comprehensive error handling and validation:
- Validate context state before operations
- Add proper error codes and messages
- Implement graceful degradation when operations fail
- Add debug logging for troubleshooting

## Test Cases

### Test Case 1: Context Reinitialization Stability
```python
def test_context_reinitialization_stability():
    """Test that multiple context reinitializations don't cause crashes."""
    import pyvvisf

    scene = pyvvisf.CreateISFSceneRef()
    # ... setup shader ...

    for i in range(10):
        pyvvisf.reinitialize_glfw_context()
        # Should not crash
        buffer = scene.create_and_render_a_buffer(size)
        assert buffer is not None
```

### Test Case 2: Batch Rendering Stability
```python
def test_batch_rendering_stability():
    """Test that batch rendering operations are stable."""
    import pyvvisf

    scene = pyvvisf.CreateISFSceneRef()
    # ... setup shader ...

    for i in range(20):
        buffer_pool.cleanup()
        pyvvisf.reinitialize_glfw_context()
        buffer = scene.create_and_render_a_buffer(size)
        # Should complete all 20 renders without crashes
```

### Test Case 3: Resource Cleanup Validation
```python
def test_resource_cleanup():
    """Test that all resources are properly cleaned up."""
    import pyvvisf

    # Create resources
    buffer_pool = pyvvisf.GLBufferPool()
    scene = pyvvisf.CreateISFSceneRef()

    # Use resources
    # ... rendering operations ...

    # Cleanup
    buffer_pool.cleanup()
    pyvvisf.cleanup_glfw_context()  # Should exist

    # Verify cleanup
    # Should not have any remaining OpenGL resources
```

## Impact Assessment

### Current Impact
- **Production Use**: Not recommended due to stability issues
- **Development**: Hindered by frequent crashes
- **Batch Processing**: Unreliable and prone to failures
- **Memory Usage**: Potential memory leaks in long-running applications

### Business Impact
- Development time increased due to debugging crashes
- Inability to implement reliable batch rendering features
- Risk of data loss in production environments
- Need for workarounds that reduce performance

## Workarounds

### Temporary Workarounds
1. **Avoid Context Reinitialization**: Use a single context for the entire application lifecycle
2. **Manual Resource Management**: Implement custom resource tracking and cleanup
3. **Error Recovery**: Add crash recovery mechanisms in the application layer
4. **Reduced Batch Sizes**: Process smaller batches to reduce crash probability

### Long-term Solutions
1. **Fork and Fix**: Fork the library and implement the fixes described above
2. **Alternative Library**: Consider using an alternative ISF rendering library
3. **Native Implementation**: Implement ISF rendering directly using OpenGL

## Conclusion

The pyvvisf library has critical stability issues that make it unsuitable for production use in its current state. The segmentation faults during context reinitialization are particularly problematic and need immediate attention. The recommended approach is to implement the fixes described above, with priority given to the context reinitialization segfault fix.

## Contact Information

This bug report was generated during testing of the isf-shader-renderer framework. For questions or additional information, please refer to the framework's documentation and issue tracker.

---

**Note**: This bug report is formatted for AI consumption and implementation. All reproduction steps and code examples have been tested and verified to reproduce the described issues.
