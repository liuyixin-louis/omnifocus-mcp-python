# Codex Installation Guide for OmniFocus MCP Server

## ✅ Tested and Verified Configuration

This configuration has been tested and confirmed working on macOS with Codex.

## Configuration for OpenAI Codex

Codex uses TOML configuration for MCP servers. The configuration file is located at:
- **macOS/Linux**: `~/.codex/config.toml`
- **Windows**: `%USERPROFILE%\.codex\config.toml`

### Option 1: Using System Python (if 3.11+ installed)

```toml
[mcp_servers.omnifocus]
command = "python3"
args = ["/path/to/omnifocus-mcp-python/src/omnifocus_server.py"]
# Optional: Increase timeout for initial connection
startup_timeout_sec = 20
# Optional: Increase timeout for OmniFocus operations
tool_timeout_sec = 30
```

### Option 2: Using Specific Python Path

```toml
[mcp_servers.omnifocus]
# For Homebrew Python on Apple Silicon
command = "/opt/homebrew/bin/python3.11"
args = ["/path/to/omnifocus-mcp-python/src/omnifocus_server.py"]

# Or for Intel Macs / system Python
# command = "/usr/local/bin/python3.11"
# args = ["/path/to/omnifocus-mcp-python/src/omnifocus_server.py"]
```

### Option 3: Using Git Clone

First, clone the repository:
```bash
cd ~/Documents
git clone https://github.com/liuyixin-louis/omnifocus-mcp-python.git
```

Then add to Codex config:
```toml
[mcp_servers.omnifocus]
command = "python3"
args = ["~/Documents/omnifocus-mcp-python/src/omnifocus_server.py"]
```

### Option 4: Using Virtual Environment

If you prefer to use a virtual environment:

1. Set up the environment:
```bash
cd /path/to/omnifocus-mcp-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure in Codex:
```toml
[mcp_servers.omnifocus]
command = "/path/to/omnifocus-mcp-python/venv/bin/python"
args = ["/path/to/omnifocus-mcp-python/src/omnifocus_server.py"]
```

## Working Example Configuration (Tested)

Here's the exact configuration that has been tested and verified to work:

```toml
# Add this section to your ~/.codex/config.toml file

[mcp_servers.omnifocus]
command = "/usr/local/bin/python3.11"
args = ["/Users/apple/Desktop/workspace/mcp-local/omnifocus-mcp-enhanced/python-omnifocus-mcp/src/omnifocus_server.py"]
startup_timeout_sec = 20
tool_timeout_sec = 30
```

Replace the path in `args` with your actual path to the omnifocus_server.py file.

## Verifying the Installation

After adding the configuration:

1. **Restart Codex** (if it was running)
2. **Test the connection** by asking Codex to use OmniFocus tools
3. **Check logs** if there are issues: `~/.codex/log/`

The server communicates via STDIO using the MCP protocol, so it will only respond when Codex sends requests.

## Troubleshooting

### 1. Python Version Issues

Ensure Python 3.11+ is installed:
```bash
python3 --version
```

If not, install it:
```bash
# macOS with Homebrew
brew install python@3.11

# Or use pyenv
pyenv install 3.11.9
pyenv local 3.11.9
```

### 2. Missing Dependencies

Install required packages:
```bash
# For the Python version you're using
/usr/local/bin/python3.11 -m pip install "mcp[cli]"
```

### 3. Path Issues

Use absolute paths in the configuration:
```toml
# Good - absolute path
args = ["/Users/username/Desktop/omnifocus-mcp-python/src/omnifocus_server.py"]

# Bad - relative path (may not work)
args = ["~/omnifocus-mcp-python/src/omnifocus_server.py"]
```

### 4. Permission Issues

Ensure Codex/Terminal has automation permissions:
- System Settings → Privacy & Security → Automation
- Enable permissions for your terminal/IDE to control OmniFocus

### 5. Testing the Server

Test the server manually before adding to Codex:
```bash
# Should hang (waiting for JSON-RPC input) - this is normal
python3 /path/to/omnifocus_server.py
```

Press Ctrl+C to exit.

## Available Tools

Once configured, you'll have access to 25 tools:

### Core Operations
- `add_task` - Create tasks with rich attributes
- `add_project` - Create projects
- `edit_task` - Modify existing tasks
- `remove_task` - Delete tasks

### Queries
- `get_inbox_tasks` - List inbox items
- `get_flagged_tasks` - Show flagged tasks
- `get_forecast_tasks` - View forecast
- `filter_tasks` - Advanced filtering

### Batch Operations
- `batch_add_tasks` - Create multiple tasks
- `batch_complete_tasks` - Complete multiple tasks

### Advanced
- `list_custom_perspectives` - View perspectives
- `dump_database` - Export full database

## Example Usage in Codex

Once configured, you can use natural language:
- "Add a task to OmniFocus: Meeting at 3pm tomorrow"
- "Show my flagged tasks"
- "Create a new project called Q1 Goals"
- "Mark task XYZ as complete"

## Notes

- The server uses STDIO transport (default for Codex)
- No additional environment variables required
- The server is stateless - each request is independent
- All operations are performed via OmniJS automation

## Repository

Latest version and updates:
https://github.com/liuyixin-louis/omnifocus-mcp-python

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure OmniFocus is running
3. Check the GitHub repository for updates
4. Open an issue on GitHub if needed