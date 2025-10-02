# Repository Summary: omnifocus-mcp-python

## 📦 Repository Status
- **GitHub URL**: https://github.com/liuyixin-louis/omnifocus-mcp-python
- **Status**: ✅ Fully synchronized with GitHub
- **Latest Commit**: Python symlink issue documentation
- **Total Files**: 12 tracked files

## 📁 Repository Contents

### Core Files
- `src/omnifocus_server.py` - Main MCP server implementation (25 tools)
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Project configuration
- `test_server.py` - Test suite
- `.gitignore` - Git ignore rules
- `LICENSE` - MIT License

### Documentation
- `README.md` - Main documentation with installation guides
- `MCP_INTEGRATION_PATTERNS.md` - Comprehensive integration patterns for Claude Code & Codex
- `CODEX_INSTALLATION.md` - Specific guide for OpenAI Codex
- `FASTMCP_DEVELOPMENT_GUIDE.md` - FastMCP development patterns
- `PYTHON_DEVELOPMENT_GUIDE.md` - Original Python MCP development guide
- `IMPLEMENTATION_SUMMARY.md` - Project implementation overview

## 🚀 Key Features

### 25 Implemented Tools
- Task Creation: `add_task`, `add_project`
- Task Queries: `get_inbox_tasks`, `get_flagged_tasks`, `get_forecast_tasks`, etc.
- Task Modification: `edit_task`, `edit_project`, `remove_task`, `remove_project`
- Batch Operations: `batch_add_tasks`, `batch_complete_tasks`
- Advanced: `filter_tasks`, `list_custom_perspectives`, `get_custom_perspective_tasks`
- Export: `dump_database`, `list_projects`, `list_tags`

### Platform Support
- ✅ Claude Desktop (JSON config)
- ✅ Claude Code (CLI installation)
- ✅ OpenAI Codex (TOML config)
- ✅ Other MCP-compatible clients

## 🔧 Installation Quick Start

### Claude Code
```bash
claude mcp add omnifocus-python /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 /path/to/omnifocus-mcp-python/src/omnifocus_server.py
```

### Codex
```toml
[mcp_servers.omnifocus]
command = "/usr/local/bin/python3.11"
args = ["/path/to/omnifocus-mcp-python/src/omnifocus_server.py"]
```

## 📈 Repository Stats
- Language: Python 3.11+
- Framework: FastMCP
- Protocol: MCP (Model Context Protocol)
- Integration: OmniFocus via OmniJS/JXA

## 🔗 Important Links
- GitHub: https://github.com/liuyixin-louis/omnifocus-mcp-python
- MCP Protocol: https://modelcontextprotocol.io/
- FastMCP: https://github.com/jlowin/fastmcp
- OmniFocus Automation: https://omni-automation.com/

## ✅ Quality Assurance
- All tests passing
- MyPy type checking clean
- Comprehensive error handling
- Production-ready code
- Tested on macOS with OmniFocus 4

---
*Last Updated: October 2, 2024*