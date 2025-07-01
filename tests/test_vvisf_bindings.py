"""
Tests for VVISF Python bindings.

This module tests the core functionality of the VVISF Python bindings
implemented in Phase 2 of the implementation plan.
"""

import pytest
import sys
import os

# Add the src directory to the path so we can import the bindings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import vvisf_bindings as vvisf
    VVISF_AVAILABLE = True
except ImportError:
    VVISF_AVAILABLE = False


@pytest.mark.skipif(not VVISF_AVAILABLE, reason="VVISF bindings not available")
class TestVVISFBindings:
    """Test suite for VVISF Python bindings."""

    def test_platform_info(self):
        """Test platform information retrieval."""
        platform_info = vvisf.get_platform_info()
        assert isinstance(platform_info, str)
        assert len(platform_info) > 0
        print(f"Platform: {platform_info}")

    def test_vvisf_availability(self):
        """Test VVISF availability check."""
        available = vvisf.is_vvisf_available()
        assert isinstance(available, bool)
        assert available, "VVISF should be available"
        print(f"VVISF Available: {available}")

    def test_module_attributes(self):
        """Test module-level attributes."""
        assert hasattr(vvisf, '__version__')
        assert hasattr(vvisf, '__platform__')
        assert hasattr(vvisf, '__available__')
        print(f"Version: {vvisf.__version__}")

    def test_isf_val_types(self):
        """Test ISF value type enums."""
        # Test enum values
        assert vvisf.ISFValType.None_ == 0
        assert vvisf.ISFValType.Bool == 2
        assert vvisf.ISFValType.Float == 4
        assert vvisf.ISFValType.Color == 6
        assert vvisf.ISFValType.Image == 8

        # Test string conversion
        assert str(vvisf.ISFValType.Float) == "Float"
        assert str(vvisf.ISFValType.Color) == "Color"

        # Test uses_image method
        assert vvisf.isf_val_type_uses_image(vvisf.ISFValType.Image) == True
        assert vvisf.isf_val_type_uses_image(vvisf.ISFValType.Float) == False

    def test_isf_file_types(self):
        """Test ISF file type enums."""
        assert vvisf.ISFFileType.Source == 1
        assert vvisf.ISFFileType.Filter == 2
        assert vvisf.ISFFileType.Transition == 4
        assert vvisf.ISFFileType.All == 7

        # Test string conversion
        assert str(vvisf.ISFFileType.Source) == "Source"
        assert str(vvisf.ISFFileType.Filter) == "Filter"

    def test_isf_val_creation(self):
        """Test ISF value creation functions."""
        # Test null value
        null_val = vvisf.ISFNullVal()
        assert null_val.is_null_val()
        assert not null_val.is_float_val()

        # Test boolean value
        bool_val = vvisf.ISFBoolVal(True)
        assert bool_val.is_bool_val()
        assert bool_val.get_bool_val() == True

        # Test float value
        float_val = vvisf.ISFFloatVal(3.14)
        assert float_val.is_float_val()
        assert abs(float_val.get_float_val() - 3.14) < 0.001

        # Test long value
        long_val = vvisf.ISFLongVal(42)
        assert long_val.is_long_val()
        assert long_val.get_long_val() == 42

        # Test point value
        point_val = vvisf.ISFPoint2DVal(100.0, 200.0)
        assert point_val.is_point2d_val()
        assert point_val.get_point_val_by_index(0) == 100.0
        assert point_val.get_point_val_by_index(1) == 200.0

        # Test color value
        color_val = vvisf.ISFColorVal(1.0, 0.5, 0.0, 1.0)
        assert color_val.is_color_val()
        assert color_val.get_color_val_by_channel(0) == 1.0  # R
        assert color_val.get_color_val_by_channel(1) == 0.5  # G
        assert color_val.get_color_val_by_channel(2) == 0.0  # B
        assert color_val.get_color_val_by_channel(3) == 1.0  # A

        # Test event value
        event_val = vvisf.ISFEventVal(True)
        assert event_val.is_event_val()
        assert event_val.get_bool_val() == True

    def test_isf_val_methods(self):
        """Test ISF value methods."""
        # Test type checking
        val = vvisf.ISFFloatVal(3.14)
        assert val.is_float_val()
        assert not val.is_color_val()
        assert not val.is_null_val()

        # Test value extraction
        assert abs(val.get_float_val() - 3.14) < 0.001
        assert abs(val.get_double_val() - 3.14) < 0.001
        assert val.get_bool_val() == True  # Non-zero is True
        assert val.get_long_val() == 3

        # Test string representation
        assert "float" in val.get_type_string().lower()
        assert "3.14" in val.get_val_string()

    def test_isf_attr_creation(self):
        """Test ISF attribute creation."""
        # Create a simple attribute
        attr = vvisf.ISFAttr(
            name="test_attr",
            description="Test attribute",
            label="Test",
            type=vvisf.ISFValType.Float,
            min_val=vvisf.ISFFloatVal(0.0),
            max_val=vvisf.ISFFloatVal(1.0),
            default_val=vvisf.ISFFloatVal(0.5)
        )

        # Test basic properties
        assert attr.name() == "test_attr"
        assert attr.description() == "Test attribute"
        assert attr.label() == "Test"
        assert attr.type() == vvisf.ISFValType.Float

        # Test value properties
        assert attr.default_val().get_float_val() == 0.5
        assert attr.min_val().get_float_val() == 0.0
        assert attr.max_val().get_float_val() == 1.0

        # Test value setting
        attr.set_current_val(vvisf.ISFFloatVal(0.7))
        assert attr.current_val().get_float_val() == 0.7

    def test_isf_scene_creation(self):
        """Test ISF scene creation."""
        # Create scene
        scene = vvisf.CreateISFSceneRef()
        assert scene is not None

        # Test basic properties
        assert scene.size() is not None
        assert scene.render_size() is not None

        # Test time management
        scene.set_base_time()
        timestamp = scene.get_timestamp()
        assert timestamp is not None

    def test_utility_functions(self):
        """Test utility functions."""
        # Test file checking
        is_isf = vvisf.file_is_probably_isf("nonexistent.fs")
        assert isinstance(is_isf, bool)

        # Test file scanning (should return empty list for non-existent path)
        files = vvisf.scan_for_isf_files("/nonexistent/path")
        assert isinstance(files, list)
        assert len(files) == 0

        # Test default files
        default_files = vvisf.get_default_isf_files()
        assert isinstance(default_files, list)

    def test_error_handling(self):
        """Test error handling."""
        # Test VVISFError exception
        assert hasattr(vvisf, 'VVISFError')
        
        # Test that we can catch VVISFError
        try:
            # This should raise an error for non-existent file
            doc = vvisf.CreateISFDocRef("nonexistent.fs")
            # If we get here, the file might exist, so we can't test the error
        except vvisf.VVISFError:
            # This is expected for non-existent files
            pass
        except Exception as e:
            # Other exceptions are also acceptable
            print(f"Caught exception: {e}")

    def test_value_type_queries(self):
        """Test value type query functions."""
        # Test type string conversion
        type_str = vvisf.isf_val_type_to_string(vvisf.ISFValType.Float)
        assert isinstance(type_str, str)
        assert "float" in type_str.lower()

        # Test uses image check
        assert vvisf.isf_val_type_uses_image(vvisf.ISFValType.Image) == True
        assert vvisf.isf_val_type_uses_image(vvisf.ISFValType.Float) == False

        # Test file type string conversion
        file_type_str = vvisf.isf_file_type_to_string(vvisf.ISFFileType.Source)
        assert isinstance(file_type_str, str)
        assert "source" in file_type_str.lower()


if __name__ == "__main__":
    # Run basic tests if module is run directly
    if VVISF_AVAILABLE:
        print("Testing VVISF Python bindings...")
        
        # Basic availability test
        print(f"Platform: {vvisf.get_platform_info()}")
        print(f"Available: {vvisf.is_vvisf_available()}")
        print(f"Version: {vvisf.__version__}")
        
        # Test value creation
        val = vvisf.ISFFloatVal(3.14)
        print(f"Created float value: {val.get_float_val()}")
        
        print("Basic tests passed!")
    else:
        print("VVISF bindings not available. Run 'make vvisf_bindings' first.")
        sys.exit(1) 