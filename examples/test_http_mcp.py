#!/usr/bin/env python3
"""Test script for HTTP MCP server with MCP protocol messages."""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPHTTPClient:
    """Client for testing MCP protocol over HTTP."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_mcp_message(self, method: str, params: Optional[Dict[str, Any]] = None, msg_id: int = 1) -> Dict[str, Any]:
        """Send an MCP protocol message to the server."""
        message = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method
        }
        if params:
            message["params"] = params
        
        logger.info(f"Sending MCP message: {method}")
        logger.debug(f"Message: {json.dumps(message, indent=2)}")
        
        if self.session is None:
            raise RuntimeError("Session not initialized")
        
        async with self.session.post(
            self.base_url,
            json=message,
            headers={"Content-Type": "application/json"}
        ) as response:
            result = await response.json()
            logger.info(f"Received response for {method}: {response.status}")
            logger.debug(f"Response: {json.dumps(result, indent=2)}")
            return result

async def test_mcp_protocol():
    """Test MCP protocol over HTTP."""
    async with MCPHTTPClient() as client:
        logger.info("=== Testing MCP Protocol over HTTP ===")
        
        # Test 1: Initialize
        logger.info("\n1. Testing initialize...")
        init_response = await client.send_mcp_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": True,
                "resources": True
            },
            "clientInfo": {
                "name": "cursor",
                "version": "1.0.0"
            }
        })
        
        if "result" in init_response:
            logger.info("✅ Initialize successful")
            logger.info(f"Server: {init_response['result']['serverInfo']}")
        else:
            logger.error(f"❌ Initialize failed: {init_response}")
            return
        
        # Test 2: List tools
        logger.info("\n2. Testing tools/list...")
        tools_response = await client.send_mcp_message("tools/list")
        
        if "result" in tools_response and "tools" in tools_response["result"]:
            tools = tools_response["result"]["tools"]
            logger.info(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                logger.info(f"  - {tool['name']}: {tool['description']}")
        else:
            logger.error(f"❌ Tools list failed: {tools_response}")
            return
        
        # Test 3: Validate shader
        logger.info("\n3. Testing tools/call (validate_shader)...")
        test_shader = """/*{
    "DESCRIPTION": "Test shader",
    "CREDIT": "Test",
    "CATEGORIES": ["Test"],
    "INPUTS": []
}*/
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}"""
        
        validate_response = await client.send_mcp_message("tools/call", {
            "name": "validate_shader",
            "arguments": {
                "shader_content": test_shader
            }
        })
        
        if "result" in validate_response:
            logger.info("✅ Shader validation successful")
            logger.info(f"Result: {validate_response['result']}")
        else:
            logger.error(f"❌ Shader validation failed: {validate_response}")
        
        # Test 4: Get shader info
        logger.info("\n4. Testing tools/call (get_shader_info)...")
        info_response = await client.send_mcp_message("tools/call", {
            "name": "get_shader_info",
            "arguments": {
                "shader_content": test_shader
            }
        })
        
        if "result" in info_response:
            logger.info("✅ Shader info extraction successful")
            logger.info(f"Result: {info_response['result']}")
        else:
            logger.error(f"❌ Shader info extraction failed: {info_response}")
        
        # Test 5: Render shader (small test)
        logger.info("\n5. Testing tools/call (render_shader)...")
        render_response = await client.send_mcp_message("tools/call", {
            "name": "render_shader",
            "arguments": {
                "shader_content": test_shader,
                "time_codes": [0.0],
                "width": 320,
                "height": 240
            }
        })
        
        if "result" in render_response:
            logger.info("✅ Shader rendering successful")
            result = render_response["result"]
            if "content" in result:
                logger.info(f"Content type: {type(result['content'])}")
                if isinstance(result["content"], list) and len(result["content"]) > 0:
                    content = result["content"][0]
                    logger.info(f"Content type: {content.get('type')}")
                    if content.get("type") == "image":
                        logger.info(f"Image saved to: {content.get('uri')}")
                    elif content.get("type") == "text":
                        logger.info(f"Text response: {content.get('text')[:200]}...")
        else:
            logger.error(f"❌ Shader rendering failed: {render_response}")
        
        # Test 6: List resources
        logger.info("\n6. Testing resources/list...")
        resources_response = await client.send_mcp_message("resources/list")
        
        if "result" in resources_response and "resources" in resources_response["result"]:
            resources = resources_response["result"]["resources"]
            logger.info(f"✅ Found {len(resources)} resources:")
            for resource in resources:
                logger.info(f"  - {resource['uri']}: {resource['name']}")
        else:
            logger.error(f"❌ Resources list failed: {resources_response}")
        
        logger.info("\n=== MCP Protocol Test Complete ===")

async def test_health_endpoint():
    """Test the health endpoint."""
    async with aiohttp.ClientSession() as session:
        logger.info("\n=== Testing Health Endpoint ===")
        
        async with session.get("http://localhost:8000/health") as response:
            if response.status == 200:
                result = await response.json()
                logger.info(f"✅ Health check successful: {result}")
            else:
                logger.error(f"❌ Health check failed: {response.status}")

async def main():
    """Main test function."""
    try:
        # Test health endpoint first
        await test_health_endpoint()
        
        # Test MCP protocol
        await test_mcp_protocol()
        
    except aiohttp.ClientConnectorError:
        logger.error("❌ Could not connect to server. Make sure the server is running on http://localhost:8000")
        logger.info("Start the server with: isf-mcp-server --http --port 8000 --debug")
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 