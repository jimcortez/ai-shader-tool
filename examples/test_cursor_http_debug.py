#!/usr/bin/env python3
"""Test script to simulate Cursor's HTTP requests for debugging."""

import requests
import json
import time

def test_cursor_http_requests():
    """Test various HTTP requests that Cursor might send."""
    base_url = "http://localhost:8000"
    
    print("Testing Cursor-like HTTP requests...")
    print("=" * 50)
    
    # Test 1: GET root endpoint
    print("\n1. Testing GET /")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: POST root endpoint (this is what Cursor might be doing)
    print("\n2. Testing POST /")
    try:
        response = requests.post(f"{base_url}/", json={"test": "data"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: POST with MCP-like data
    print("\n3. Testing POST / with MCP-like data")
    mcp_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "cursor",
                "version": "1.0.0"
            }
        }
    }
    try:
        response = requests.post(f"{base_url}/", json=mcp_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: POST to /render endpoint
    print("\n4. Testing POST /render")
    render_data = {
        "shader_content": "/*{ \"DESCRIPTION\": \"Test\" }*/ void main() { gl_FragColor = vec4(1.0); }",
        "time_codes": [0.0],
        "width": 320,
        "height": 240
    }
    try:
        response = requests.post(f"{base_url}/render", json=render_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: GET /health
    print("\n5. Testing GET /health")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cursor_http_requests() 