#!/usr/bin/env python3
"""Test script using the official MCP Python client to test the FastMCP server."""

import asyncio
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession


async def test_fastmcp_server():
    """Test the FastMCP server using the official MCP client."""
    print("Testing FastMCP server with official MCP client...")
    
    # Create server parameters
    server_params = StdioServerParameters(command="isf-mcp-server")
    
    try:
        # Use the official MCP client
        async with stdio_client(server_params) as (read_stream, write_stream):
            # Create a client session
            session = ClientSession(read_stream, write_stream)
            
            # Initialize the session
            print("Initializing session...")
            init_result = await session.initialize()
            print(f"Session initialized: {init_result}")
            
            # List tools
            print("\nListing tools...")
            tools_result = await session.list_tools()
            print(f"Available tools: {len(tools_result.tools)}")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test tool call
            if tools_result.tools:
                print("\nTesting tool call...")
                first_tool = tools_result.tools[0]
                result = await session.call_tool(
                    name=first_tool.name,
                    arguments={"shader_content": "void main() { gl_FragColor = vec4(1.0); }"}
                )
                print(f"Tool call result: {result}")
            
            print("\nTest completed successfully!")
            
    except Exception as e:
        print(f"Error during test: {e}")
        raise


def main():
    """Main function."""
    try:
        asyncio.run(test_fastmcp_server())
        print("\n✅ Test passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 