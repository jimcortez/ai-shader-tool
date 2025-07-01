#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <string>
#include <memory>
#include <vector>
#include <map>

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

// Helper function to convert ISFValType to string
std::string isf_val_type_to_string(VVISF::ISFValType type) {
    return VVISF::StringFromISFValType(type);
}

// Helper function to check if ISFValType uses image
bool isf_val_type_uses_image(VVISF::ISFValType type) {
    return VVISF::ISFValTypeUsesImage(type);
}

// Helper function to convert ISFFileType to string
std::string isf_file_type_to_string(VVISF::ISFFileType type) {
    return VVISF::ISFFileTypeString(type);
}

// Helper function to scan for ISF files
std::vector<std::string> scan_for_isf_files(const std::string& folder_path, 
                                           VVISF::ISFFileType file_type = VVISF::ISFFileType_None, 
                                           bool recursive = true) {
    auto files = VVISF::CreateArrayOfISFsForPath(folder_path, file_type, recursive);
    if (files) {
        return *files;
    }
    return {};
}

// Helper function to get default ISF files
std::vector<std::string> get_default_isf_files(VVISF::ISFFileType file_type = VVISF::ISFFileType_None) {
    auto files = VVISF::CreateArrayOfDefaultISFs(file_type);
    if (files) {
        return *files;
    }
    return {};
}

// Helper function to check if file is probably an ISF
bool file_is_probably_isf(const std::string& path) {
    return VVISF::FileIsProbablyAnISF(path);
}

PYBIND11_MODULE(vvisf_bindings, m) {
    m.doc() = "Python bindings for VVISF library - ISF shader rendering"; // Optional module docstring
    
    // Exception class
    py::register_exception<VVISFError>(m, "VVISFError");
    
    // Enums - must be registered before functions that use them as default arguments
    py::enum_<VVISF::ISFValType>(m, "ISFValType")
        .value("None_", VVISF::ISFValType_None)
        .value("Event", VVISF::ISFValType_Event)
        .value("Bool", VVISF::ISFValType_Bool)
        .value("Long", VVISF::ISFValType_Long)
        .value("Float", VVISF::ISFValType_Float)
        .value("Point2D", VVISF::ISFValType_Point2D)
        .value("Color", VVISF::ISFValType_Color)
        .value("Cube", VVISF::ISFValType_Cube)
        .value("Image", VVISF::ISFValType_Image)
        .value("Audio", VVISF::ISFValType_Audio)
        .value("AudioFFT", VVISF::ISFValType_AudioFFT)
        .def("__str__", &isf_val_type_to_string);
    
    py::enum_<VVISF::ISFFileType>(m, "ISFFileType")
        .value("None_", VVISF::ISFFileType_None)
        .value("Source", VVISF::ISFFileType_Source)
        .value("Filter", VVISF::ISFFileType_Filter)
        .value("Transition", VVISF::ISFFileType_Transition)
        .value("All", VVISF::ISFFileType_All)
        .def("__str__", &isf_file_type_to_string);
    
    // Module-level functions
    m.def("get_platform_info", &get_platform_info, "Get platform information");
    m.def("is_vvisf_available", &is_vvisf_available, "Check if VVISF is available");
    m.def("scan_for_isf_files", &scan_for_isf_files, 
          "Scan for ISF files in a directory",
          py::arg("folder_path"), 
          py::arg("file_type") = VVISF::ISFFileType_None, 
          py::arg("recursive") = true);
    m.def("get_default_isf_files", &get_default_isf_files,
          "Get default ISF files",
          py::arg("file_type") = VVISF::ISFFileType_None);
    m.def("file_is_probably_isf", &file_is_probably_isf,
          "Check if a file is probably an ISF file",
          py::arg("path"));
    m.def("isf_val_type_to_string", &isf_val_type_to_string, "Convert ISFValType to string");
    m.def("isf_val_type_uses_image", &isf_val_type_uses_image, "Check if ISFValType uses image");
    m.def("isf_file_type_to_string", &isf_file_type_to_string, "Convert ISFFileType to string");
    
    // ISFVal class
    py::class_<VVISF::ISFVal>(m, "ISFVal")
        .def(py::init<>())
        .def(py::init<VVISF::ISFValType>())
        .def(py::init<VVISF::ISFValType, bool>())
        .def(py::init<VVISF::ISFValType, int32_t>())
        .def(py::init<VVISF::ISFValType, double>())
        .def(py::init<VVISF::ISFValType, double, double>())
        .def(py::init<VVISF::ISFValType, double, double, double, double>())
        .def("type", &VVISF::ISFVal::type)
        .def("get_double_val", &VVISF::ISFVal::getDoubleVal)
        .def("get_bool_val", &VVISF::ISFVal::getBoolVal)
        .def("get_long_val", &VVISF::ISFVal::getLongVal)
        .def("get_point_val_by_index", &VVISF::ISFVal::getPointValByIndex)
        .def("set_point_val_by_index", &VVISF::ISFVal::setPointValByIndex)
        .def("get_color_val_by_channel", &VVISF::ISFVal::getColorValByChannel)
        .def("set_color_val_by_channel", &VVISF::ISFVal::setColorValByChannel)
        .def("image_buffer", &VVISF::ISFVal::imageBuffer)
        .def("set_image_buffer", &VVISF::ISFVal::setImageBuffer)
        .def("get_type_string", &VVISF::ISFVal::getTypeString)
        .def("get_val_string", &VVISF::ISFVal::getValString)
        .def("is_null_val", &VVISF::ISFVal::isNullVal)
        .def("is_event_val", &VVISF::ISFVal::isEventVal)
        .def("is_bool_val", &VVISF::ISFVal::isBoolVal)
        .def("is_long_val", &VVISF::ISFVal::isLongVal)
        .def("is_float_val", &VVISF::ISFVal::isFloatVal)
        .def("is_point2d_val", &VVISF::ISFVal::isPoint2DVal)
        .def("is_color_val", &VVISF::ISFVal::isColorVal)
        .def("is_cube_val", &VVISF::ISFVal::isCubeVal)
        .def("is_image_val", &VVISF::ISFVal::isImageVal)
        .def("is_audio_val", &VVISF::ISFVal::isAudioVal)
        .def("is_audio_fft_val", &VVISF::ISFVal::isAudioFFTVal)
        .def("__str__", &VVISF::ISFVal::getValString);
    
    // ISFVal creation functions
    m.def("ISFNullVal", &VVISF::ISFNullVal, "Create a null ISFVal");
    m.def("ISFEventVal", &VVISF::ISFEventVal, "Create an event ISFVal", py::arg("value") = false);
    m.def("ISFBoolVal", &VVISF::ISFBoolVal, "Create a boolean ISFVal");
    m.def("ISFLongVal", &VVISF::ISFLongVal, "Create a long ISFVal");
    m.def("ISFFloatVal", &VVISF::ISFFloatVal, "Create a float ISFVal");
    m.def("ISFPoint2DVal", &VVISF::ISFPoint2DVal, "Create a Point2D ISFVal");
    m.def("ISFColorVal", &VVISF::ISFColorVal, "Create a color ISFVal");
    m.def("ISFImageVal", &VVISF::ISFImageVal, "Create an image ISFVal");
    
    // ISFAttr class
    py::class_<VVISF::ISFAttr, std::shared_ptr<VVISF::ISFAttr>>(m, "ISFAttr")
        .def(py::init<const std::string&, const std::string&, const std::string&, 
                      VVISF::ISFValType, const VVISF::ISFVal&, const VVISF::ISFVal&, 
                      const VVISF::ISFVal&, const VVISF::ISFVal&, 
                      const std::vector<std::string>*, const std::vector<int32_t>*>(),
             py::arg("name"), py::arg("description"), py::arg("label"), py::arg("type"),
             py::arg("min_val") = VVISF::ISFNullVal(), py::arg("max_val") = VVISF::ISFNullVal(),
             py::arg("default_val") = VVISF::ISFNullVal(), py::arg("identity_val") = VVISF::ISFNullVal(),
             py::arg("labels") = nullptr, py::arg("values") = nullptr)
        .def("name", &VVISF::ISFAttr::name)
        .def("description", &VVISF::ISFAttr::description)
        .def("label", &VVISF::ISFAttr::label)
        .def("type", &VVISF::ISFAttr::type)
        .def("current_val", &VVISF::ISFAttr::currentVal)
        .def("set_current_val", &VVISF::ISFAttr::setCurrentVal)
        .def("update_and_get_eval_variable", &VVISF::ISFAttr::updateAndGetEvalVariable)
        .def("should_have_image_buffer", &VVISF::ISFAttr::shouldHaveImageBuffer)
        .def("get_current_image_buffer", &VVISF::ISFAttr::getCurrentImageBuffer)
        .def("set_current_image_buffer", &VVISF::ISFAttr::setCurrentImageBuffer)
        .def("min_val", &VVISF::ISFAttr::minVal)
        .def("max_val", &VVISF::ISFAttr::maxVal)
        .def("default_val", &VVISF::ISFAttr::defaultVal)
        .def("identity_val", &VVISF::ISFAttr::identityVal)
        .def("label_array", &VVISF::ISFAttr::labelArray)
        .def("val_array", &VVISF::ISFAttr::valArray)
        .def("is_filter_input_image", &VVISF::ISFAttr::isFilterInputImage)
        .def("set_is_filter_input_image", &VVISF::ISFAttr::setIsFilterInputImage)
        .def("is_trans_start_image", &VVISF::ISFAttr::isTransStartImage)
        .def("set_is_trans_start_image", &VVISF::ISFAttr::setIsTransStartImage)
        .def("is_trans_end_image", &VVISF::ISFAttr::isTransEndImage)
        .def("set_is_trans_end_image", &VVISF::ISFAttr::setIsTransEndImage)
        .def("is_trans_progress_float", &VVISF::ISFAttr::isTransProgressFloat)
        .def("set_is_trans_progress_float", &VVISF::ISFAttr::setIsTransProgressFloat)
        .def("clear_uniform_locations", &VVISF::ISFAttr::clearUniformLocations)
        .def("set_uniform_location", &VVISF::ISFAttr::setUniformLocation)
        .def("get_uniform_location", &VVISF::ISFAttr::getUniformLocation)
        .def("get_attr_description", &VVISF::ISFAttr::getAttrDescription)
        .def("__str__", &VVISF::ISFAttr::getAttrDescription);
    
    // ISFDoc class
    py::class_<VVISF::ISFDoc, std::shared_ptr<VVISF::ISFDoc>>(m, "ISFDoc")
        .def(py::init<const std::string&, VVISF::ISFScene*, bool>(),
             py::arg("path"), py::arg("parent_scene") = nullptr, py::arg("throw_except") = true)
        .def(py::init<const std::string&, const std::string&, const std::string&, 
                      VVISF::ISFScene*, bool>(),
             py::arg("fs_contents"), py::arg("vs_contents"), py::arg("imports_dir"),
             py::arg("parent_scene") = nullptr, py::arg("throw_except") = true)
        // File properties
        .def("path", &VVISF::ISFDoc::path)
        .def("name", &VVISF::ISFDoc::name)
        .def("description", &VVISF::ISFDoc::description)
        .def("credit", &VVISF::ISFDoc::credit)
        .def("vsn", &VVISF::ISFDoc::vsn)
        .def("type", &VVISF::ISFDoc::type)
        .def("categories", &VVISF::ISFDoc::categories)
        // Input attributes
        .def("inputs", &VVISF::ISFDoc::inputs)
        .def("image_inputs", &VVISF::ISFDoc::imageInputs)
        .def("audio_inputs", &VVISF::ISFDoc::audioInputs)
        .def("image_imports", &VVISF::ISFDoc::imageImports)
        .def("inputs_of_type", &VVISF::ISFDoc::inputsOfType)
        .def("input", &VVISF::ISFDoc::input)
        // Render pass getters
        .def("render_passes", &VVISF::ISFDoc::renderPasses)
        .def("get_buffer_for_key", &VVISF::ISFDoc::getBufferForKey)
        .def("get_persistent_buffer_for_key", &VVISF::ISFDoc::getPersistentBufferForKey)
        .def("get_temp_buffer_for_key", &VVISF::ISFDoc::getTempBufferForKey)
        // Source code getters (wrap std::string* as std::string)
        .def("json_source_string", [](const VVISF::ISFDoc& self) { auto ptr = self.jsonSourceString(); return ptr ? *ptr : std::string(); })
        .def("json_string", [](const VVISF::ISFDoc& self) { auto ptr = self.jsonString(); return ptr ? *ptr : std::string(); })
        .def("vert_shader_source", [](const VVISF::ISFDoc& self) { auto ptr = self.vertShaderSource(); return ptr ? *ptr : std::string(); })
        .def("frag_shader_source", [](const VVISF::ISFDoc& self) { auto ptr = self.fragShaderSource(); return ptr ? *ptr : std::string(); })
        // Utility methods
        .def("set_parent_scene", &VVISF::ISFDoc::setParentScene)
        .def("parent_scene", &VVISF::ISFDoc::parentScene)
        .def("generate_texture_type_string", &VVISF::ISFDoc::generateTextureTypeString)
        .def("generate_shader_source", &VVISF::ISFDoc::generateShaderSource)
        .def("eval_buffer_dimensions_with_render_size", &VVISF::ISFDoc::evalBufferDimensionsWithRenderSize);
    
    // ISFDoc creation functions
    m.def("CreateISFDocRef", &VVISF::CreateISFDocRef, 
          "Create an ISFDoc from file path",
          py::arg("path"), py::arg("parent_scene") = nullptr, py::arg("throw_except") = true);
    m.def("CreateISFDocRefWith", &VVISF::CreateISFDocRefWith,
          "Create an ISFDoc from shader strings",
          py::arg("fs_contents"), py::arg("imports_dir") = "/", 
          py::arg("vs_contents") = std::string(VVISF::ISFVertPassthru_GL2),
          py::arg("parent_scene") = nullptr, py::arg("throw_except") = true);
    
    // ISFScene class
    py::class_<VVISF::ISFScene, std::shared_ptr<VVISF::ISFScene>>(m, "ISFScene")
        .def(py::init<>())
        .def(py::init<const VVGL::GLContextRef&>())
        .def("prepare_to_be_deleted", &VVISF::ISFScene::prepareToBeDeleted)
        // Loading ISF files
        .def("use_file", [](VVISF::ISFScene& self) { self.useFile(); })
        .def("use_file_with_path", [](VVISF::ISFScene& self, const std::string& path, bool throw_exc, bool reset_timer) { self.useFile(path, throw_exc, reset_timer); })
        .def("use_doc", &VVISF::ISFScene::useDoc)
        .def("doc", &VVISF::ISFScene::doc)
        // Uncommon setters/getters
        .def("set_always_render_to_float", &VVISF::ISFScene::setAlwaysRenderToFloat)
        .def("always_render_to_float", &VVISF::ISFScene::alwaysRenderToFloat)
        .def("set_persistent_to_iosurface", &VVISF::ISFScene::setPersistentToIOSurface)
        .def("persistent_to_iosurface", &VVISF::ISFScene::persistentToIOSurface)
        // Setting/getting images and values
        .def("set_buffer_for_input_named", &VVISF::ISFScene::setBufferForInputNamed)
        .def("set_filter_input_buffer", &VVISF::ISFScene::setFilterInputBuffer)
        .def("set_buffer_for_input_image_key", &VVISF::ISFScene::setBufferForInputImageKey)
        .def("set_buffer_for_audio_input_key", &VVISF::ISFScene::setBufferForAudioInputKey)
        .def("get_buffer_for_image_input", &VVISF::ISFScene::getBufferForImageInput)
        .def("get_buffer_for_audio_input", &VVISF::ISFScene::getBufferForAudioInput)
        .def("get_persistent_buffer_named", &VVISF::ISFScene::getPersistentBufferNamed)
        .def("get_temp_buffer_named", &VVISF::ISFScene::getTempBufferNamed)
        .def("set_value_for_input_named", &VVISF::ISFScene::setValueForInputNamed)
        .def("value_for_input_named", &VVISF::ISFScene::valueForInputNamed)
        // Rendering (bind only the simplest overload)
        .def("create_and_render_a_buffer", [](VVISF::ISFScene& self, const VVGL::Size& size) { return self.createAndRenderABuffer(size); })
        // Size and time management
        .def("set_size", &VVISF::ISFScene::setSize)
        .def("size", &VVISF::ISFScene::size)
        .def("render_size", &VVISF::ISFScene::renderSize)
        .def("get_timestamp", &VVISF::ISFScene::getTimestamp)
        .def("set_throw_exceptions", &VVISF::ISFScene::setThrowExceptions)
        .def("set_base_time", &VVISF::ISFScene::setBaseTime)
        .def("base_time", &VVISF::ISFScene::baseTime)
        // Getting attributes/INPUTS
        .def("input_named", &VVISF::ISFScene::inputNamed)
        .def("inputs", &VVISF::ISFScene::inputs)
        .def("inputs_of_type", &VVISF::ISFScene::inputsOfType)
        .def("image_inputs", &VVISF::ISFScene::imageInputs)
        .def("audio_inputs", &VVISF::ISFScene::audioInputs)
        .def("image_imports", &VVISF::ISFScene::imageImports);
    
    // ISFScene creation functions
    m.def("CreateISFSceneRef", &VVISF::CreateISFSceneRef, "Create an ISFScene");
    m.def("CreateISFSceneRefUsing", &VVISF::CreateISFSceneRefUsing, "Create an ISFScene with GL context");
    
    // Basic module info
    m.attr("__version__") = "0.2.0";
    m.attr("__platform__") = get_platform_info();
    m.attr("__available__") = is_vvisf_available();
} 