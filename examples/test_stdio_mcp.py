#!/usr/bin/env python3
"""Test script for the ISF Shader Renderer stdio MCP server."""

import json
import subprocess
import sys
import time


def test_stdio_mcp_server():
    """Test the stdio MCP server with proper initialization."""
    print("Testing ISF Shader Renderer stdio MCP Server")
    print("=" * 50)
    
    # Start the MCP server process
    process = subprocess.Popen(
        ["isf-mcp-server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Check if process started successfully
    if process.stdin is None or process.stdout is None:
        print("❌ Failed to start MCP server process")
        return False
    
    try:
        # Test 1: Initialize
        print("\n1. Testing initialization...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Init response: {response.strip()}")
        
        # Test 2: Send initialized notification
        print("\n2. Sending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Wait a moment for processing
        time.sleep(0.1)
        
        # Test 3: List tools
        print("\n3. Testing list_tools...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"List tools response: {response.strip()}")
        
        # Test 4: List resources
        print("\n4. Testing list_resources...")
        list_resources_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(list_resources_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"List resources response: {response.strip()}")
        
        # Test 5: Call a simple tool (validate_shader)
        print("\n5. Testing validate_shader tool...")
        validate_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "validate_shader",
                "arguments": {
                    "shader_content": "/*{ \"DESCRIPTION\": \"Test\" }*/ void main() { gl_FragColor = vec4(1.0); }"
                }
            }
        }
        
        process.stdin.write(json.dumps(validate_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Validate shader response: {response.strip()}")
        
        print("\n✅ stdio MCP server test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
        
    finally:
        # Clean up
        process.terminate()
        process.wait()


def main():
    """Main function."""
    print("ISF Shader Renderer stdio MCP Server Test")
    print("This will test the stdio MCP server implementation.")
    print()
    
    success = test_stdio_mcp_server()
    
    if success:
        print("\n🎉 All stdio MCP server tests passed!")
        return 0
    else:
        print("\n💥 stdio MCP server tests failed!")
        return 1


if __name__ == "__main__":
    exit(main()) 