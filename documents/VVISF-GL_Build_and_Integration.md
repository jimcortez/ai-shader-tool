# Building and Integrating VVISF-GL with Python Bindings

## Overview
This document explains the process of building the VVISF-GL library and configuring it for use as a dynamically linked dependency in a Python project via pybind11 bindings. The steps are tailored for macOS but can be adapted for Linux and Windows with minor changes.

---

## 1. VVISF-GL Library Structure
- **Location:** `external/VVISF-GL/`
- **Components:**
  - `VVGL/`: Core OpenGL utilities and buffer management
  - `VVISF/`: ISF (Interactive Shader Format) rendering logic
  - `examples/`: Sample applications and platform-specific projects
- **Dependencies:**
  - OpenGL (platform-specific frameworks/libraries)
  - C++11 or later
  - (macOS) Foundation, ImageIO, IOSurface, CoreGraphics, CoreVideo, CoreMedia, AppKit frameworks

---

## 2. Building the VVISF-GL Library

### a. Using the Provided Makefile
1. **Navigate to the VVISF directory:**
   ```sh
   cd external/VVISF-GL/VVISF
   ```
2. **Build the library:**
   ```sh
   make
   ```
   This will:
   - Build the VVGL static library (`VVGL/bin/libVVGL.a`)
   - Build the VVISF static and dynamic libraries (`VVISF/bin/libVVISF.a`, `VVISF/bin/libVVISF.dylib`)

### b. Platform-Specific Notes
- **macOS:**
  - The Makefile automatically sets the correct compiler flags and links against the required frameworks.
  - If you encounter errors about missing frameworks, ensure Xcode command line tools are installed.
- **Linux/Windows:**
  - You may need to adjust the Makefile or use CMake for proper library and dependency paths.

---

## 3. Configuring the Python Project to Link VVISF-GL

### a. CMake Integration
- The main project uses CMake to manage building and linking.
- The CMake configuration:
  - Checks for the existence of the pre-built static libraries:
    - `${PROJECT_ROOT}/external/VVISF-GL/VVGL/bin/libVVGL.a`
    - `${PROJECT_ROOT}/external/VVISF-GL/VVISF/bin/libVVISF.a`
  - Adds them as imported static libraries:
    ```cmake
    add_library(VVGL STATIC IMPORTED)
    set_target_properties(VVGL PROPERTIES IMPORTED_LOCATION ${VVGL_LIBRARY})
    add_library(VVISF STATIC IMPORTED)
    set_target_properties(VVISF PROPERTIES IMPORTED_LOCATION ${VVISF_LIBRARY})
    ```
  - Sets the include directories for VVGL and VVISF headers:
    ```cmake
    include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}/external/VVISF-GL/VVGL/include
        ${CMAKE_CURRENT_SOURCE_DIR}/external/VVISF-GL/VVISF/include
    )
    ```
  - Links the required macOS frameworks for OpenGL and image handling:
    ```cmake
    set(PLATFORM_LIBS
        "-framework Foundation"
        "-framework ImageIO"
        "-framework OpenGL"
        "-framework IOSurface"
        "-framework CoreGraphics"
        "-framework CoreVideo"
        "-framework CoreMedia"
        "-framework AppKit"
    )
    ```

### b. Python Bindings with pybind11
- The project uses `pybind11` to expose C++ classes and functions to Python.
- The CMake configuration attempts to find `pybind11`:
    ```cmake
    find_package(pybind11 QUIET)
    if(pybind11_FOUND)
        pybind11_add_module(vvisf_bindings src/vvisf_bindings.cpp)
        target_link_libraries(vvisf_bindings PRIVATE VVISF VVGL ${PLATFORM_LIBS})
    endif()
    ```
- The resulting Python module (`vvisf_bindings.so`) is placed in `src/isf_shader_renderer/` for import by the main Python code.

---

## 4. Troubleshooting
- **Linker errors about missing symbols:**
  - Ensure all required frameworks are linked (see above for macOS).
  - Make sure the static libraries are built for the correct architecture (e.g., arm64 vs x86_64).
- **Cannot find pybind11:**
  - Install pybind11 via pip or your package manager, or set `pybind11_DIR` in CMake.
- **OpenGL context errors:**
  - VVGL and VVISF require an active OpenGL context before creating buffers or rendering. This must be handled in the C++ or Python code before using these features.

---

## 5. Summary of Steps
1. Build VVISF-GL using the provided Makefile.
2. Configure CMake to use the resulting static libraries and include directories.
3. Link all required platform libraries/frameworks.
4. Build the Python bindings with pybind11 (if available).
5. Ensure an OpenGL context is created before using VVISF/VVGL features in Python or C++.

---

## References
- [VVISF-GL GitHub](https://github.com/Vidvox/VVISF-GL)
- [ISF Specification](https://github.com/mrRay/ISF_Spec)
- [pybind11 Documentation](https://pybind11.readthedocs.io/en/stable/) 