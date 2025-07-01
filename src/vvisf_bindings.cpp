#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <string>
#include <memory>

// VVISF includes
#include "VVISF.hpp"
#include "VVGL.hpp"

namespace py = pybind11;

// Platform detection function
std::string get_platform_info() {
#ifdef VVGL_SDK_MAC
    return std::string("macOS (VVGL_SDK_MAC)");
#elif defined(VVGL_SDK_GLFW)
    return std::string("GLFW (VVGL_SDK_GLFW)");
#elif defined(VVGL_SDK_RPI)
    return std::string("Raspberry Pi (VVGL_SDK_RPI)");
#else
    return std::string("Unknown platform");
#endif
}

// Check if VVISF is available
bool is_vvisf_available() {
    try {
        // Try to create a basic VVISF object to test availability
        auto scene = VVISF::CreateISFSceneRef();
        return scene != nullptr;
    } catch (...) {
        return false;
    }
}

// Basic error handling wrapper
class VVISFError : public std::exception {
public:
    explicit VVISFError(const std::string& message) : message_(message) {}
    
    const char* what() const noexcept override {
        return message_.c_str();
    }
    
private:
    std::string message_;
};

PYBIND11_MODULE(vvisf_bindings, m) {
    m.doc() = "Python bindings for VVISF library"; // Optional module docstring
    
    // Module-level functions
    m.def("get_platform_info", &get_platform_info, "Get platform information");
    m.def("is_vvisf_available", &is_vvisf_available, "Check if VVISF is available");
    
    // Exception class
    py::register_exception<VVISFError>(m, "VVISFError");
    
    // Basic module info
    m.attr("__version__") = "0.1.0";
    m.attr("__platform__") = get_platform_info();
    m.attr("__available__") = is_vvisf_available();
} 