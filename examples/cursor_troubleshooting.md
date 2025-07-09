# Cursor MCP Integration Troubleshooting Guide

## Overview

This guide helps troubleshoot issues when enabling the ISF Shader Renderer MCP server in Cursor.

## Common Issues and Solutions

### 1. "Loading tools" message times out

**Symptoms:**
- Cursor shows "Loading tools..." message
- Message never disappears or times out
- No tools appear in the MCP panel

**Possible Causes:**
- MCP server not starting properly
- Incorrect Cursor configuration
- Network/firewall issues (if using HTTP mode)
- Permission issues

**Solutions:**

#### A. Check MCP Server Installation
```bash
# Verify the MCP server is installed and accessible
which isf-mcp-server

# Check available options
isf-mcp-server --help

# Test the server directly (stdio mode - default)
isf-mcp-server --stdio
# (Should start and wait for input - this is normal)
# Press Ctrl+C to exit

# Test HTTP mode
isf-mcp-server --http --port 8000
# (Should start HTTP server)
```

#### B. Verify Cursor Configuration
Make sure your Cursor configuration includes the correct MCP server setup:

**For stdio mode (recommended):**
```json
{
  "mcpServers": {
    "isf-shader-renderer": {
      "command": "isf-mcp-server",
      "args": ["--stdio"]
    }
  }
}
```

**For HTTP mode:**
```json
{
  "mcpServers": {
    "isf-shader-renderer": {
      "command": "isf-mcp-server",
      "args": ["--http", "--port", "8000"]
    }
  }
}
```

#### C. Test MCP Server Manually
Run the test script to verify the server works:
```bash
python examples/test_cursor_mcp.py
```

### 2. "Invalid request parameters" errors

**Symptoms:**
- Cursor shows error messages about invalid parameters
- MCP server logs show validation errors

**Solutions:**
- The MCP server has been updated to handle all request formats correctly
- Make sure you're using the latest version of the package
- Restart Cursor after updating the MCP server

### 3. Server fails to start

**Symptoms:**
- Cursor cannot start the MCP server
- Error messages about missing dependencies

**Solutions:**

#### A. Check Dependencies
```bash
# Install required dependencies
pip install -e .

# Verify MCP dependencies
pip list | grep mcp
```

#### B. Check Python Environment
Make sure Cursor is using the same Python environment where the MCP server is installed:
```bash
# Check which Python Cursor is using
which python

# Verify the MCP server is in the same environment
which isf-mcp-server
```

### 4. Permission Issues

**Symptoms:**
- Server cannot write to temp directories
- File access errors

**Solutions:**
```bash
# Check temp directory permissions
ls -la /tmp/isf_renderer

# Create temp directory if it doesn't exist
mkdir -p /tmp/isf_renderer
chmod 755 /tmp/isf_renderer
```

### 5. Large Image Rendering Issues

**Symptoms:**
- Rendering fails for large images
- Timeout errors during rendering

**Solutions:**
- The server now uses file-based output to avoid stdio limitations
- Large images are saved to disk instead of returned via stdio
- Check the `/tmp/isf_renderer/` directory for rendered files

## Debugging Steps

### 1. Enable Verbose Logging
Start the MCP server with verbose output:
```bash
isf-mcp-server --verbose
```

### 2. Check Cursor Logs
Look for MCP-related errors in Cursor's developer console:
- Open Cursor
- Press `Cmd+Shift+I` (Mac) or `Ctrl+Shift+I` (Windows/Linux)
- Check the Console tab for errors

### 3. Test Server Manually
Use the provided test scripts:
```bash
# Test stdio mode
python examples/test_stdio_mcp.py

# Test Cursor-like behavior
python examples/test_cursor_mcp.py

# Test HTTP mode
python examples/test_http_server.py
```

### 4. Check Server Process
Verify the MCP server is running:
```bash
ps aux | grep isf-mcp-server
```

## Configuration Examples

### Basic stdio Configuration (Recommended)
```json
{
  "mcpServers": {
    "isf-shader-renderer": {
      "command": "isf-mcp-server",
      "args": ["--stdio"]
    }
  }
}
```

### HTTP Configuration
```json
{
  "mcpServers": {
    "isf-shader-renderer": {
      "command": "isf-mcp-server",
      "args": ["--http", "--port", "8000"]
    }
  }
}
```

### With Custom Python Path
```json
{
  "mcpServers": {
    "isf-shader-renderer": {
      "command": "/path/to/python",
      "args": ["-m", "isf_shader_renderer.mcp.server"]
    }
  }
}
```

## Available Tools

Once the MCP server is working, you'll have access to these tools:

1. **render_shader** - Render ISF shaders to PNG images
2. **validate_shader** - Validate ISF shader syntax
3. **get_shader_info** - Extract shader information

## Available Resources

The server provides example shaders:
- `isf://examples/basic` - Basic ISF shader example
- `isf://examples/animated` - Animated ISF shader example  
- `isf://examples/gradient` - Gradient ISF shader example

## Getting Help

If you're still experiencing issues:

1. Run the test scripts to verify the server works
2. Check Cursor's developer console for error messages
3. Verify your Cursor configuration matches the examples above
4. Make sure all dependencies are installed correctly
5. Try restarting Cursor after making configuration changes

## Recent Fixes

The following issues have been resolved:
- ✅ Pydantic deprecation warnings (`.dict()` → `.model_dump()`)
- ✅ Resource format compatibility
- ✅ HTTP server response format
- ✅ File-based image rendering for large images
- ✅ Proper MCP protocol compliance
- ✅ Timeout handling and error recovery 