#!/usr/bin/env python3
"""Debug script for resource reading."""

import asyncio
from isf_shader_renderer.mcp.handlers import ISFShaderHandlers

async def debug_resources():
    handlers = ISFShaderHandlers()
    
    # List resources
    resources = await handlers.list_resources()
    print(f"Found {len(resources)} resources:")
    for i, resource in enumerate(resources):
        print(f"  {i}: {repr(resource.uri)} - {resource.name}")
    
    # Try to read the first resource
    if resources:
        first_uri = resources[0].uri
        print(f"\nTrying to read: {repr(first_uri)}")
        try:
            content = await handlers.read_resource(first_uri)
            print(f"Success! Content length: {len(content)} bytes")
            print(f"First 100 chars: {content[:100].decode()}")
        except Exception as e:
            print(f"Error: {e}")
            print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(debug_resources()) 