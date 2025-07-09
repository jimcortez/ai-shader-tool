#!/usr/bin/env python3
"""Test script for the ISF Shader Renderer HTTP server."""

import asyncio
import json
import requests
import base64
from pathlib import Path
from PIL import Image
import io


class ISFHTTPClient:
    """HTTP client for testing the ISF Shader Renderer HTTP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the HTTP client."""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> dict:
        """Check server health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_server_info(self) -> dict:
        """Get server information."""
        response = self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()
    
    def render_shader(self, shader_content: str, time_codes: list, width: int = 320, height: int = 240, quality: int = 95) -> dict:
        """Render a shader via HTTP."""
        payload = {
            "shader_content": shader_content,
            "time_codes": time_codes,
            "width": width,
            "height": height,
            "quality": quality,
            "verbose": True
        }
        
        response = self.session.post(f"{self.base_url}/render", json=payload)
        response.raise_for_status()
        return response.json()
    
    def validate_shader(self, shader_content: str) -> dict:
        """Validate a shader via HTTP."""
        payload = {
            "shader_content": shader_content
        }
        
        response = self.session.post(f"{self.base_url}/validate", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_shader_info(self, shader_content: str) -> dict:
        """Get shader information via HTTP."""
        payload = {
            "shader_content": shader_content
        }
        
        response = self.session.post(f"{self.base_url}/info", json=payload)
        response.raise_for_status()
        return response.json()
    
    def list_resources(self) -> dict:
        """List available resources."""
        response = self.session.get(f"{self.base_url}/resources")
        response.raise_for_status()
        return response.json()
    
    def read_resource(self, resource_uri: str) -> str:
        """Read a resource."""
        response = self.session.get(f"{self.base_url}/resources/{resource_uri}")
        response.raise_for_status()
        return response.text


def test_http_server():
    """Test the HTTP server functionality."""
    print("Testing ISF Shader Renderer HTTP Server")
    print("=" * 50)
    
    # Test shader
    test_shader = """/*{
        "DESCRIPTION": "Test HTTP Shader",
        "CREDIT": "Generated for HTTP testing"
    }*/
    void main() {
        vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
        
        // Create a simple animated pattern
        float time = TIME;
        vec3 color = vec3(
            sin(uv.x * 10.0 + time * 2.0) * 0.5 + 0.5,
            cos(uv.y * 8.0 + time * 1.5) * 0.5 + 0.5,
            sin((uv.x + uv.y) * 5.0 + time * 3.0) * 0.5 + 0.5
        );
        
        gl_FragColor = vec4(color, 1.0);
    }"""
    
    client = ISFHTTPClient()
    
    try:
        # Test 1: Health check
        print("\n1. Testing health check...")
        health = client.health_check()
        print(f"Health: {health}")
        
        # Test 2: Server info
        print("\n2. Testing server info...")
        info = client.get_server_info()
        print(f"Server: {info['name']} v{info['version']}")
        print(f"Endpoints: {info['endpoints']}")
        
        # Test 3: Shader validation
        print("\n3. Testing shader validation...")
        validation = client.validate_shader(test_shader)
        print(f"Validation success: {validation['success']}")
        print(f"Message: {validation['message']}")
        if validation.get('errors'):
            print(f"Errors: {validation['errors']}")
        if validation.get('warnings'):
            print(f"Warnings: {validation['warnings']}")
        
        # Test 4: Shader info
        print("\n4. Testing shader info extraction...")
        shader_info = client.get_shader_info(test_shader)
        print(f"Info success: {shader_info['success']}")
        if shader_info.get('shader_info'):
            info = shader_info['shader_info']
            print(f"Shader type: {info.get('type')}")
            print(f"Size: {info.get('size')} characters")
            print(f"Lines: {info.get('lines')}")
            print(f"Has TIME uniform: {info.get('has_time_uniform')}")
            print(f"Has RENDERSIZE uniform: {info.get('has_resolution_uniform')}")
        
        # Test 5: Resource listing
        print("\n5. Testing resource listing...")
        resources = client.list_resources()
        print(f"Available resources: {len(resources['resources'])}")
        for resource in resources['resources']:
            print(f"  - {resource['name']}: {resource['description']}")
        
        # Test 6: Resource reading
        print("\n6. Testing resource reading...")
        if resources['resources']:
            first_resource = resources['resources'][0]
            resource_uri = first_resource['uri'].replace('isf://', '')
            content = client.read_resource(resource_uri)
            print(f"Resource content length: {len(content)} characters")
            print(f"First 100 chars: {content[:100]}")
        
        # Test 7: Shader rendering (file-based)
        print("\n7. Testing shader rendering (file-based)...")
        render_result = client.render_shader(
            shader_content=test_shader,
            time_codes=[0.0, 1.0, 2.0],
            width=320,
            height=240,
            quality=95
        )
        
        print(f"Render success: {render_result['success']}")
        print(f"Message: {render_result['message']}")
        print(f"Rendered frames: {len(render_result.get('rendered_frames', []))}")
        
        # Display file information
        if render_result.get('metadata', {}).get('rendered_files'):
            print("\nRendered files:")
            for file_info in render_result['metadata']['rendered_files']:
                print(f"  - {file_info['filename']}: {file_info['size']} bytes")
                print(f"    Path: {file_info['path']}")
                print(f"    Time: {file_info['time_code']}s")
        
        # Test 8: Verify files exist
        print("\n8. Verifying rendered files...")
        if render_result.get('metadata', {}).get('output_directory'):
            output_dir = Path(render_result['metadata']['output_directory'])
            if output_dir.exists():
                files = list(output_dir.glob("*.png"))
                print(f"Found {len(files)} PNG files in {output_dir}")
                for file_path in files:
                    print(f"  - {file_path.name}: {file_path.stat().st_size} bytes")
                    
                    # Try to open and verify the image
                    try:
                        with Image.open(file_path) as img:
                            print(f"    Image size: {img.size}")
                            print(f"    Image mode: {img.mode}")
                    except Exception as e:
                        print(f"    Error reading image: {e}")
            else:
                print(f"Output directory not found: {output_dir}")
        
        print("\n✅ HTTP server test completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection failed. Make sure the HTTP server is running:")
        print("   isf-mcp-server --port 8000")
        return False
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True


def main():
    """Main function."""
    print("ISF Shader Renderer HTTP Server Test")
    print("This will test the HTTP server implementation.")
    print()
    
    success = test_http_server()
    
    if success:
        print("\n🎉 All HTTP server tests passed!")
        return 0
    else:
        print("\n💥 HTTP server tests failed!")
        return 1


if __name__ == "__main__":
    exit(main()) 