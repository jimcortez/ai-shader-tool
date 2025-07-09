#!/usr/bin/env python3
"""Test script for FastMCP HTTP server."""

import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_fastmcp_endpoints():
    """Test different endpoints on the FastMCP server."""
    async with aiohttp.ClientSession() as session:
        base_url = "http://localhost:8000"
        
        # Test different endpoints
        endpoints = ["/", "/mcp", "/api", "/v1", "/health", "/docs", "/openapi.json"]
        
        for endpoint in endpoints:
            try:
                logger.info(f"Testing endpoint: {endpoint}")
                
                # Try GET request
                async with session.get(f"{base_url}{endpoint}") as response:
                    logger.info(f"GET {endpoint}: {response.status}")
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"Content: {content[:200]}...")
                
                # Try POST request with MCP message
                mcp_message = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "1.0"}
                    }
                }
                
                async with session.post(
                    f"{base_url}{endpoint}",
                    json=mcp_message,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                ) as response:
                    logger.info(f"POST {endpoint}: {response.status}")
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"Response: {content[:200]}...")
                    elif response.status != 404:
                        content = await response.text()
                        logger.info(f"Error response: {content[:200]}...")
                        
            except Exception as e:
                logger.error(f"Error testing {endpoint}: {e}")

async def test_mcp_protocol():
    """Test MCP protocol communication."""
    async with aiohttp.ClientSession() as session:
        # Try the standard MCP endpoint
        mcp_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": True,
                    "resources": True
                },
                "clientInfo": {"name": "cursor", "version": "1.0.0"}
            }
        }
        
        try:
            logger.info("Testing MCP protocol on /mcp endpoint...")
            async with session.post(
                "http://localhost:8000/mcp",
                json=mcp_message,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            ) as response:
                logger.info(f"MCP initialize response: {response.status}")
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"Response: {content}")
                else:
                    content = await response.text()
                    logger.error(f"Error: {content}")
                    
        except Exception as e:
            logger.error(f"Error in MCP protocol test: {e}")

async def main():
    """Main test function."""
    logger.info("=== Testing FastMCP HTTP Server ===")
    
    # Test endpoints
    await test_fastmcp_endpoints()
    
    # Test MCP protocol
    await test_mcp_protocol()
    
    logger.info("=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main()) 