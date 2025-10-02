# MCP Integration Patterns: Claude Code & Codex

A comprehensive guide to successfully integrating MCP servers with AI coding assistants.

## Table of Contents
1. [Overview](#overview)
2. [Claude Code Integration](#claude-code-integration)
3. [Codex Integration](#codex-integration)
4. [Common Patterns](#common-patterns)
5. [Troubleshooting Framework](#troubleshooting-framework)
6. [Testing Strategy](#testing-strategy)

---

## Overview

MCP (Model Context Protocol) servers bridge AI assistants with external tools and services. This guide provides proven patterns for successful integration.

### Key Success Factors
1. **Python Version**: Use Python 3.11+ (3.10 minimum for MCP package)
2. **Absolute Paths**: Always use full paths, never relative
3. **Dependencies**: Install MCP package for your specific Python version
4. **Permissions**: Ensure automation permissions are granted

---

## Claude Code Integration

### Pattern 1: Direct CLI Installation ✅

**Most Reliable Method**:
```bash
claude mcp add <server-name> <python-path> <server-script-path>
```

**Example**:
```bash
claude mcp add omnifocus-python /usr/local/bin/python3.11 /Users/username/omnifocus-mcp-python/src/omnifocus_server.py
```

### Pattern 2: JSON Configuration

**For Complex Setups**:
```bash
claude mcp add-json <server-name> '{
  "command": "<python-path>",
  "args": ["<server-script-path>"],
  "env": {}
}'
```

### Key Steps for Claude Code

1. **Check Python Version**:
   ```bash
   python3 --version  # Must be 3.10+
   which python3.11   # Find specific version
   ```

2. **Install MCP Package**:
   ```bash
   # For specific Python version
   /usr/local/bin/python3.11 -m pip install "mcp[cli]"
   ```

3. **Add Server**:
   ```bash
   claude mcp add <name> <python> <script>
   ```

4. **Verify**:
   ```bash
   claude mcp list  # Should show "✓ Connected"
   ```

5. **Troubleshoot if Failed**:
   ```bash
   # Remove and re-add
   claude mcp remove <name>
   claude mcp add <name> <python> <script>
   ```

### Configuration Storage
- **Project-specific**: `.mcp.json` in project root
- **Global**: `~/.claude.json`

---

## Codex Integration

### Pattern: TOML Configuration ✅

**Location**: `~/.codex/config.toml`

**Template**:
```toml
[mcp_servers.<server-name>]
command = "<python-path>"
args = ["<server-script-path>"]
# Optional but recommended
startup_timeout_sec = 20
tool_timeout_sec = 30
```

**Working Example**:
```toml
[mcp_servers.omnifocus]
command = "/usr/local/bin/python3.11"
args = ["/Users/username/omnifocus-mcp-python/src/omnifocus_server.py"]
startup_timeout_sec = 20
tool_timeout_sec = 30
```

### Key Steps for Codex

1. **Locate Config File**:
   ```bash
   # macOS/Linux
   ~/.codex/config.toml
   
   # Windows
   %USERPROFILE%\.codex\config.toml
   ```

2. **Backup Existing Config**:
   ```bash
   cp ~/.codex/config.toml ~/.codex/config.toml.backup
   ```

3. **Add MCP Server Section**:
   - Edit config.toml
   - Add `[mcp_servers.<name>]` section
   - Use absolute paths

4. **Validate TOML Syntax**:
   ```bash
   python3 -c "import toml; toml.load(open('~/.codex/config.toml'))"
   ```

5. **Restart Codex**:
   - Required for config changes to take effect

---

## Common Patterns

### 1. Python Selection Strategy

```bash
# Priority order for Python selection:
1. /usr/local/bin/python3.11  # System-wide Python 3.11
2. /opt/homebrew/bin/python3.11  # Homebrew on Apple Silicon
3. python3  # System default (if 3.10+)
4. Virtual environment Python  # Project-specific
```

### 2. Path Resolution Pattern

**Always Use Absolute Paths**:
```bash
# ✅ Good
/Users/username/project/src/server.py

# ❌ Bad
~/project/src/server.py
./src/server.py
src/server.py
```

### 3. Dependency Installation Pattern

```bash
# Install for specific Python version
<python-path> -m pip install "mcp[cli]"

# Example
/usr/local/bin/python3.11 -m pip install "mcp[cli]"
```

### 4. Server Testing Pattern

**Before Integration**:
```bash
# Test server starts without errors
<python-path> <server-script>

# Should hang (waiting for input) - this is correct
# Press Ctrl+C to exit
```

---

## Troubleshooting Framework

### Systematic Debugging Process

1. **Version Check**:
   ```bash
   <python-path> --version  # Must be 3.10+
   ```

2. **Dependency Check**:
   ```bash
   <python-path> -m pip list | grep mcp
   ```

3. **Path Verification**:
   ```bash
   ls -la <server-script-path>  # File exists?
   ```

4. **Manual Test**:
   ```bash
   <python-path> <server-script>  # Should hang
   ```

5. **Permission Check**:
   - System Settings → Privacy & Security → Automation
   - Grant permissions to Terminal/IDE

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Python version too old" | Install Python 3.11+ via Homebrew or python.org |
| "Module 'mcp' not found" | Install for correct Python: `python3.11 -m pip install "mcp[cli]"` |
| "Server failed to start" | Use absolute paths, check file permissions |
| "No response from server" | Check automation permissions, ensure target app is running |
| "Invalid TOML syntax" | Validate with Python: `python3 -c "import toml; toml.load('config.toml')"` |

---

## Testing Strategy

### 1. Pre-Integration Test

```python
#!/usr/bin/env python3
"""test_mcp_server.py - Test MCP server before integration"""

import subprocess
import json

def test_server():
    cmd = ["<python-path>", "<server-script>"]
    
    # Test initialization
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, 
                           stdout=subprocess.PIPE, text=True)
    
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
        "id": 1
    }
    
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()
    
    response = proc.stdout.readline()
    print("Response:", response)
    
    proc.terminate()
    return bool(response)

if __name__ == "__main__":
    test_server()
```

### 2. Post-Integration Verification

**Claude Code**:
```bash
claude mcp list  # Check status
claude mcp get <server-name>  # Get details
```

**Codex**:
- Ask Codex to list available tools
- Test a simple command
- Check logs at `~/.codex/log/`

---

## Best Practices

### Development Workflow

1. **Develop & Test Locally**:
   ```bash
   python src/server.py  # Test manually
   pytest tests/  # Run tests
   ```

2. **Package with Requirements**:
   ```bash
   # requirements.txt
   mcp[cli]>=1.0.0
   ```

3. **Document Installation**:
   - Include Python version requirements
   - Provide exact commands
   - Show expected output

4. **Version Control**:
   ```bash
   # .gitignore
   __pycache__/
   *.pyc
   .env
   ```

### Server Design Patterns

1. **Use FastMCP for Simplicity**:
   ```python
   from mcp.server.fastmcp import FastMCP
   
   mcp = FastMCP("server-name", "description")
   
   @mcp.tool()
   def my_tool():
       return "result"
   ```

2. **Handle Errors Gracefully**:
   ```python
   try:
       result = perform_operation()
       return {"success": True, "result": result}
   except Exception as e:
       return {"success": False, "error": str(e)}
   ```

3. **Type Everything**:
   ```python
   from typing import Dict, List, Optional, Any
   
   def my_tool(required: str, 
               optional: Optional[int] = None) -> Dict[str, Any]:
       ...
   ```

---

## Quick Reference

### Claude Code Commands
```bash
# Add server
claude mcp add <name> <python> <script>

# List servers
claude mcp list

# Remove server
claude mcp remove <name>

# Get details
claude mcp get <name>
```

### Codex Configuration
```toml
[mcp_servers.<name>]
command = "/path/to/python"
args = ["/path/to/script.py"]
startup_timeout_sec = 20
tool_timeout_sec = 30
```

### Python Setup
```bash
# Install Python 3.11 (macOS)
brew install python@3.11

# Install MCP
python3.11 -m pip install "mcp[cli]"

# Test server
python3.11 /path/to/server.py
```

---

## Summary

### Success Formula

1. **Right Python Version** (3.11+ recommended)
2. **Absolute Paths** everywhere
3. **MCP Package** installed for correct Python
4. **Test First** before integration
5. **Verify Connection** after setup

### Platform Differences

| Aspect | Claude Code | Codex |
|--------|------------|-------|
| Config Format | CLI/JSON | TOML |
| Config Location | ~/.claude.json | ~/.codex/config.toml |
| Add Method | `claude mcp add` | Edit config file |
| Restart Needed | No | Yes |
| Verification | `claude mcp list` | Test in Codex |

---

## Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/docs)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Python MCP Package](https://pypi.org/project/mcp/)

---

*Last Updated: 2024*
*Tested with: Claude Code 0.4.15, Codex (latest), Python 3.11.x, MCP 1.15.0*