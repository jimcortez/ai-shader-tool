#!/usr/bin/env python3
"""Test script to simulate Cursor's MCP client behavior."""

import asyncio
import json
import subprocess
import sys
import time
from typing import Dict, Any, Optional


class CursorMCPClient:
    """Simulate Cursor's MCP client behavior."""
    
    def __init__(self, server_process):
        """Initialize the client with a server process."""
        self.server_process = server_process
        self.request_id = 1
        self.initialized = False
    
    def _next_id(self) -> int:
        """Get next request ID."""
        current = self.request_id
        self.request_id += 1
        return current
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a request to the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        print(f"[DEBUG] Sending request: {request_json.strip()}", file=sys.stderr)
        
        if self.server_process.stdin is None:
            raise Exception("Server stdin is None")
        
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read response with timeout
        if self.server_process.stdout is None:
            raise Exception("Server stdout is None")
        
        try:
            # Set a reasonable timeout for MCP operations
            response_line = await asyncio.wait_for(
                self.server_process.stdout.readline(),
                timeout=30.0  # 30 second timeout
            )
            response = json.loads(response_line.decode().strip())
            print(f"[DEBUG] Received response: {response}", file=sys.stderr)
            
            if "error" in response:
                raise Exception(f"MCP Error: {response['error']}")
            
            return response.get("result", {})
            
        except asyncio.TimeoutError:
            raise Exception("MCP request timed out after 30 seconds")
    
    async def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Send a notification to the MCP server (no response expected)."""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        # Send notification (no ID, no response expected)
        notification_json = json.dumps(notification) + "\n"
        print(f"[DEBUG] Sending notification: {notification_json.strip()}", file=sys.stderr)
        
        if self.server_process.stdin is None:
            raise Exception("Server stdin is None")
        
        self.server_process.stdin.write(notification_json.encode())
        await self.server_process.stdin.drain()
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP connection (Cursor-style)."""
        print("[DEBUG] Initializing MCP connection...", file=sys.stderr)
        
        result = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "clientInfo": {
                "name": "cursor",
                "version": "1.0.0"
            }
        })
        
        self.initialized = True
        return result
    
    async def send_initialized(self) -> None:
        """Send initialized notification (Cursor-style)."""
        if not self.initialized:
            raise Exception("Must initialize before sending initialized notification")
        
        print("[DEBUG] Sending initialized notification...", file=sys.stderr)
        await self.send_notification("notifications/initialized", {})
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools (Cursor-style)."""
        if not self.initialized:
            raise Exception("Must initialize before listing tools")
        
        print("[DEBUG] Listing tools...", file=sys.stderr)
        return await self.send_request("tools/list", {})
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources (Cursor-style)."""
        if not self.initialized:
            raise Exception("Must initialize before listing resources")
        
        print("[DEBUG] Listing resources...", file=sys.stderr)
        return await self.send_request("resources/list", {})
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool (Cursor-style)."""
        if not self.initialized:
            raise Exception("Must initialize before calling tools")
        
        print(f"[DEBUG] Calling tool: {name}", file=sys.stderr)
        return await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })


async def test_cursor_mcp_behavior():
    """Test the MCP server with Cursor-like behavior."""
    print("Testing MCP server with Cursor-like behavior")
    print("=" * 50)
    
    # Start the MCP server as a subprocess
    print("Starting MCP server...")
    server_process = await asyncio.create_subprocess_exec(
        "isf-mcp-server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Create client
        client = CursorMCPClient(server_process)
        
        # Test 1: Initialize (this is what Cursor does first)
        print("\n1. Testing initialization...")
        init_result = await client.initialize()
        print(f"✅ Initialization successful: {init_result.get('serverInfo', {}).get('name')}")
        
        # Test 2: Send initialized notification (Cursor does this after init)
        print("\n2. Sending initialized notification...")
        await client.send_initialized()
        print("✅ Initialized notification sent")
        
        # Test 3: List tools (Cursor does this to discover available tools)
        print("\n3. Listing tools...")
        tools_result = await client.list_tools()
        tools = tools_result.get('tools', [])
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # Test 4: List resources (Cursor does this to discover available resources)
        print("\n4. Listing resources...")
        resources_result = await client.list_resources()
        resources = resources_result.get('resources', [])
        print(f"✅ Found {len(resources)} resources:")
        for resource in resources:
            print(f"   - {resource['name']}: {resource['description']}")
        
        # Test 5: Call a simple tool (validate_shader)
        print("\n5. Testing tool call (validate_shader)...")
        test_shader = """/*{
    "DESCRIPTION": "Test Shader for Cursor"
}*/
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    gl_FragColor = vec4(uv.x, uv.y, 0.5, 1.0);
}"""
        
        validate_result = await client.call_tool("validate_shader", {
            "shader_content": test_shader
        })
        print("✅ Tool call successful")
        
        # Test 6: Call render tool (this might be where timeouts occur)
        print("\n6. Testing tool call (render_shader)...")
        render_result = await client.call_tool("render_shader", {
            "shader_content": test_shader,
            "time_codes": [0.0],  # Single frame for speed
            "width": 320,
            "height": 240
        })
        print("✅ Render tool call successful")
        
        print("\n🎉 All Cursor MCP tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        
        # Get stderr output for debugging
        if server_process.stderr:
            try:
                stderr_output = await asyncio.wait_for(server_process.stderr.read(), timeout=5.0)
                if stderr_output:
                    print(f"Server stderr: {stderr_output.decode()}")
            except asyncio.TimeoutError:
                print("Could not read server stderr (timeout)")
        
        return False
        
    finally:
        # Terminate the server
        print("\nCleaning up...")
        server_process.terminate()
        try:
            await asyncio.wait_for(server_process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            print("Server did not terminate gracefully, forcing...")
            server_process.kill()
            await server_process.wait()


def main():
    """Main function."""
    print("Cursor MCP Client Test")
    print("This simulates how Cursor would interact with the MCP server.")
    print()
    
    try:
        success = asyncio.run(test_cursor_mcp_behavior())
        if success:
            print("\n🎉 All tests passed! The MCP server should work with Cursor.")
            return 0
        else:
            print("\n💥 Tests failed! There may be issues with Cursor integration.")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 