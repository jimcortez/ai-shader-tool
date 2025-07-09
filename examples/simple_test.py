#!/usr/bin/env python3
"""Simple test to list tools from the FastMCP server."""

import asyncio
import subprocess
import json
import sys


async def simple_test():
    """Simple test using subprocess to communicate with the server."""
    print("Starting simple test...")
    
    # Start the server
    process = await asyncio.create_subprocess_exec(
        "isf-mcp-server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    if process.stdin is None or process.stdout is None:
        print("Failed to create subprocess with pipes")
        return
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        print("Sending initialize request...")
        if process.stdin:
            await process.stdin.write((json.dumps(init_request) + "\n").encode())
            await process.stdin.drain()
        
        # Read response
        if process.stdout:
            response_line = await process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        print(f"Initialize response: {response}")
        
        # Send tools/list request
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("Sending tools/list request...")
        await process.stdin.write((json.dumps(list_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read response
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        print(f"Tools list response: {response}")
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print("No tools found or error in response")
            
    except Exception as e:
        print(f"Error: {e}")
        # Get stderr output
        stderr_output = await process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output.decode()}")
    finally:
        process.terminate()
        await process.wait()


if __name__ == "__main__":
    asyncio.run(simple_test()) 