"""HTTP server implementation for ISF Shader Renderer MCP server."""

import asyncio
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .handlers import ISFShaderHandlers
from .models import RenderRequest, RenderResponse, ValidateRequest, ValidateResponse, GetShaderInfoRequest, GetShaderInfoResponse
from .config import MCPServerConfig


class ISFShaderHTTPServer:
    """HTTP server for ISF shader rendering."""
    
    def __init__(self, config: Optional[MCPServerConfig] = None):
        """Initialize the HTTP server."""
        self.config = config or MCPServerConfig()
        self.app = FastAPI(
            title="ISF Shader Renderer MCP Server",
            description="HTTP server for ISF shader rendering via MCP",
            version="1.0.0"
        )
        self.handlers = ISFShaderHandlers()
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """Setup middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.allowed_origins or ["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """Log all incoming requests."""
            logging.info(f"Request: {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
            
            # Log request body for POST requests
            if request.method == "POST":
                try:
                    body = await request.body()
                    if body:
                        logging.info(f"Request body: {body.decode()[:200]}...")  # Log first 200 chars
                except Exception as e:
                    logging.warning(f"Could not read request body: {e}")
            
            response = await call_next(request)
            logging.info(f"Response: {response.status_code} for {request.method} {request.url.path}")
            return response
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            logging.info("GET / - Root endpoint called")
            return {
                "name": "ISF Shader Renderer MCP Server",
                "version": "1.0.0",
                "description": "HTTP server for ISF shader rendering",
                "endpoints": [
                    "/render",
                    "/validate", 
                    "/info",
                    "/health"
                ]
            }
        
        @self.app.post("/")
        async def root_post(request: Request):
            """Root POST endpoint for MCP protocol messages."""
            logging.info("POST / - MCP protocol message received")
            
            try:
                # Parse the request body as JSON
                body = await request.json()
                logging.info(f"MCP message: {body}")
                
                # Handle MCP protocol messages
                if "method" in body:
                    method = body["method"]
                    params = body.get("params", {})
                    msg_id = body.get("id")
                    
                    logging.info(f"Processing MCP method: {method}")
                    
                    if method == "initialize":
                        # Handle initialize
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {
                                    "experimental": {},
                                    "resources": {"subscribe": False, "listChanged": False},
                                    "tools": {"listChanged": False}
                                },
                                "serverInfo": {
                                    "name": "isf-shader-renderer",
                                    "version": "1.10.1"
                                }
                            }
                        }
                        return response
                    
                    elif method == "tools/list":
                        # Handle tools/list
                        tools = [
                            {
                                "name": "render_shader",
                                "description": "Render an ISF shader to PNG images at specified time codes",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "shader_content": {
                                            "type": "string",
                                            "description": "ISF shader source code"
                                        },
                                        "time_codes": {
                                            "type": "array",
                                            "items": {"type": "number"},
                                            "description": "Time codes for rendering (seconds)"
                                        },
                                        "width": {
                                            "type": "integer",
                                            "default": 1920,
                                            "description": "Output width in pixels"
                                        },
                                        "height": {
                                            "type": "integer",
                                            "default": 1080,
                                            "description": "Output height in pixels"
                                        },
                                        "quality": {
                                            "type": "integer",
                                            "default": 95,
                                            "minimum": 1,
                                            "maximum": 100,
                                            "description": "PNG quality (1-100)"
                                        },
                                        "verbose": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "Enable verbose output"
                                        }
                                    },
                                    "required": ["shader_content", "time_codes"]
                                }
                            },
                            {
                                "name": "validate_shader",
                                "description": "Validate ISF shader syntax and extract metadata",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "shader_content": {
                                            "type": "string",
                                            "description": "ISF shader source code to validate"
                                        }
                                    },
                                    "required": ["shader_content"]
                                }
                            },
                            {
                                "name": "get_shader_info",
                                "description": "Extract information from ISF shader",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "shader_content": {
                                            "type": "string",
                                            "description": "ISF shader source code"
                                        }
                                    },
                                    "required": ["shader_content"]
                                }
                            }
                        ]
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {"tools": tools}
                        }
                        return response
                    
                    elif method == "tools/call":
                        # Handle tools/call
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})
                        
                        logging.info(f"Calling tool: {tool_name}")
                        
                        # Call the appropriate handler
                        result = await self.handlers.call_tool(tool_name, arguments)
                        
                        # Format response for MCP protocol
                        if "content" in result and result["content"]:
                            # For responses with content (like rendered images), return as streaming content
                            mcp_content = result["content"]
                        else:
                            # For responses without content (like validation), return as text
                            import json
                            mcp_content = [{
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }]
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "content": mcp_content,
                                "isError": not result.get("success", True)
                            }
                        }
                        return response
                    
                    elif method == "resources/list":
                        # Handle resources/list
                        resources = await self.handlers.list_resources()
                        mcp_resources = [
                            {
                                "uri": r["uri"],
                                "name": r["name"],
                                "description": r.get("description", ""),
                                "mimeType": r.get("mime_type", "text/plain")
                            }
                            for r in resources
                        ]
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {"resources": mcp_resources}
                        }
                        return response
                    
                    elif method == "resources/read":
                        # Handle resources/read
                        uri = params.get("uri")
                        if not uri:
                            raise HTTPException(status_code=400, detail="Missing uri parameter")
                        
                        content = await self.handlers.read_resource(uri)
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "contents": [{
                                    "uri": uri,
                                    "mimeType": "text/plain",
                                    "text": content.decode()
                                }]
                            }
                        }
                        return response
                    
                    else:
                        # Unknown method
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                        return response
                
                else:
                    # Not an MCP message, return error
                    return {"error": "Invalid MCP message format"}
                    
            except Exception as e:
                logging.error(f"Error processing MCP message: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id") if isinstance(body, dict) else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            logging.info("GET /health - Health check called")
            return {"status": "healthy", "service": "isf-shader-renderer"}
        
        @self.app.post("/render")
        async def render_shader(request: RenderRequest) -> RenderResponse:
            """Render ISF shader endpoint."""
            logging.info(f"POST /render - Render shader called with {len(request.time_codes)} time codes")
            try:
                # Validate request
                if len(request.time_codes) > self.config.max_frames_per_request:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Too many time codes. Maximum allowed: {self.config.max_frames_per_request}"
                    )
                
                if request.width > self.config.max_image_size or request.height > self.config.max_image_size:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Image dimensions too large. Maximum allowed: {self.config.max_image_size}x{self.config.max_image_size}"
                    )
                
                # Call handler
                result = await self.handlers.call_tool("render_shader", request.model_dump())
                
                # Convert to response model
                return RenderResponse(**result)
                
            except Exception as e:
                logging.error(f"Error rendering shader: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/validate")
        async def validate_shader(request: ValidateRequest) -> ValidateResponse:
            """Validate ISF shader endpoint."""
            logging.info("POST /validate - Validate shader called")
            try:
                result = await self.handlers.call_tool("validate_shader", request.model_dump())
                return ValidateResponse(**result)
            except Exception as e:
                logging.error(f"Error validating shader: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/info")
        async def get_shader_info(request: GetShaderInfoRequest) -> GetShaderInfoResponse:
            """Get shader info endpoint."""
            logging.info("POST /info - Get shader info called")
            try:
                result = await self.handlers.call_tool("get_shader_info", request.model_dump())
                return GetShaderInfoResponse(**result)
            except Exception as e:
                logging.error(f"Error getting shader info: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/resources")
        async def list_resources():
            """List available resources."""
            logging.info("GET /resources - List resources called")
            try:
                resources = await self.handlers.list_resources()
                return {
                    "resources": [
                        {
                            "uri": r["uri"],
                            "name": r["name"],
                            "description": r.get("description", ""),
                            "mime_type": r.get("mime_type", "text/plain")
                        }
                        for r in resources
                    ]
                }
            except Exception as e:
                logging.error(f"Error listing resources: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/resources/{resource_uri:path}")
        async def read_resource(resource_uri: str):
            """Read resource content."""
            logging.info(f"GET /resources/{resource_uri} - Read resource called")
            try:
                # Reconstruct full URI
                full_uri = f"isf://{resource_uri}"
                content = await self.handlers.read_resource(full_uri)
                return JSONResponse(
                    content=content.decode(),
                    media_type="text/plain"
                )
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                logging.error(f"Error reading resource: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            """Global exception handler."""
            logging.error(f"Unhandled exception: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": str(exc),
                    "type": type(exc).__name__
                }
            )
    
    async def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """Run the HTTP server."""
        host = host or self.config.host
        port = port or self.config.port
        
        # Setup logging
        if self.config.enable_debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=getattr(logging, self.config.log_level.upper(), logging.INFO))
        
        # Run server
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level=self.config.log_level.lower(),
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()


def main():
    """Main entry point for HTTP server."""
    import typer
    
    app = typer.Typer()
    
    @app.command()
    def run(
        host: str = typer.Option("localhost", "--host", help="Server host"),
        port: int = typer.Option(8000, "--port", help="Server port"),
        debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
        log_level: str = typer.Option("INFO", "--log-level", help="Log level")
    ):
        """Run the ISF Shader Renderer HTTP server."""
        config = MCPServerConfig(
            host=host,
            port=port,
            enable_http=True,
            enable_debug=debug,
            log_level=log_level
        )
        
        server = ISFShaderHTTPServer(config)
        asyncio.run(server.run())
    
    app()


if __name__ == "__main__":
    main() 