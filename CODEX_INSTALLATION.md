# Codex Installation Guide for OmniFocus MCP Server

## Configuration for OpenAI Codex

Codex uses TOML configuration for MCP servers. Add the following to your Codex configuration file.

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

## Complete Example Configuration

Here's a complete example with all options:

```toml
# OmniFocus MCP Server Configuration for Codex
[mcp_servers.omnifocus]
# Command to run Python interpreter
command = "/usr/local/bin/python3.11"

# Path to the server script
args = ["/Users/username/Desktop/omnifocus-mcp-python/src/omnifocus_server.py"]

# Optional: Environment variables (if needed for future extensions)
env = { }

# Optional: Increase startup timeout (default is 10s)
# Useful if OmniFocus takes time to respond initially
startup_timeout_sec = 20

# Optional: Increase tool execution timeout (default is 60s)
# Some OmniFocus operations might take longer with large databases
tool_timeout_sec = 45
```

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