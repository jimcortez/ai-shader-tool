# AI Coding Documentation

This document is for AI agents and developers working on the internals of the AI Shader Tool codebase. It contains implementation plans, build/troubleshooting notes, code structure, and development guidelines.

## Table of Contents
1. [Implementation Plan](#implementation-plan)
2. [Build & Troubleshooting](#build--troubleshooting)
3. [Code Structure](#code-structure)
4. [Python API Notes](#python-api-notes)
5. [Platform Abstraction](#platform-abstraction)
6. [Testing](#testing)

---

## 1. Implementation Plan

See [../IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) for the full, up-to-date implementation plan, including completed and future phases.

## 2. Build & Troubleshooting

- See [VVISF-GL_Build_and_Integration.md](VVISF-GL_Build_and_Integration.md) for build instructions and troubleshooting tips.
- Common issues:
  - Pybind11 not found: install with `brew install pybind11` or `apt-get install pybind11-dev`.
  - Eigen errors: remove unnecessary includes from C++ bindings.
  - OpenGL/GLFW context issues: ensure context is created and current before buffer/image operations.
  - Segfaults: usually due to missing context or incorrect pointer usage in bindings.

## 3. Code Structure

- `src/isf_shader_renderer/renderer.py`: High-level Python API and CLI logic.
- `src/isf_shader_renderer/platform.py`: Platform abstraction, context management, and fallback logic.
- `src/isf_shader_renderer/config.py`: ShaderRendererConfig system and YAML parsing.
- `src/isf_shader_renderer/vvisf_bindings.cpp`: Pybind11 C++ bindings for VVISF-GL.
- `documents/`: All developer and advanced user documentation.

## 4. Python API Notes

- The high-level API is in `ShaderRenderer` (see [PYTHON_API.md](PYTHON_API.md)).
- Low-level VVISF bindings are in `isf_shader_renderer.vvisf_bindings`.
- Always check for VVISF/OpenGL/GLFW availability before using advanced features.
- Use the platform/context helpers in `platform.py` for safe context management.

## 5. Platform Abstraction

- All context management is handled via GLFW in C++ and Python.
- Fallback rendering is automatic if dependencies are missing.
- Platform checks and helpers are in `platform.py`.

## 6. Testing

- Run all tests with `make test`.
- Coverage reports are generated in `htmlcov/`.
- Add new tests in `tests/` for new features or bugfixes.

---

For further details, see the linked documents and code comments. 

ShaderRendererConfig: Main configuration class for the renderer. 