# OmniFocus MCP Server (Python)

A Python implementation of an MCP (Model-Context Protocol) server for OmniFocus, providing comprehensive task management capabilities through OmniJS automation.

## Features

### Core Task Management
- **Create**: Add tasks and projects with rich attributes (due dates, defer dates, tags, notes, flags)
- **Query**: Retrieve tasks from inbox, flagged items, forecast, completed today, by tag, or by ID
- **Edit**: Modify task and project properties
- **Remove**: Delete tasks and projects
- **Batch Operations**: Process multiple tasks efficiently

### Advanced Features
- **Custom Perspectives**: List and fetch tasks from custom perspectives
- **Filtering Engine**: Query tasks with flexible criteria
- **Database Export**: Full JSON export of OmniFocus data

## Installation

### Prerequisites
- macOS with OmniFocus 3 or later installed
- Python 3.11 or higher
- pip or uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd python-omnifocus-mcp
```

2. Install dependencies:

Using pip:
```bash
pip install -r requirements.txt
```

Using uv:
```bash
uv venv
uv pip install -r requirements.txt
```

Or install directly from pyproject.toml:
```bash
pip install -e .
```

## Usage

### Running the Server

For development and testing:
```bash
# Using mcp dev command for interactive testing
mcp dev src/omnifocus_server.py

# Or run directly
python src/omnifocus_server.py
```

### Configure with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "omnifocus": {
      "command": "python",
      "args": ["/path/to/python-omnifocus-mcp/src/omnifocus_server.py"],
      "env": {}
    }
  }
}
```

## Available Tools

### Task Creation
- `add_task` - Create a new task with flexible attributes
- `add_project` - Create a new project

### Task Queries
- `get_inbox_tasks` - Retrieve inbox tasks
- `get_flagged_tasks` - Get all flagged tasks
- `get_forecast_tasks` - Get forecast view tasks
- `get_completed_today` - Tasks completed today
- `get_task_by_id` - Fetch specific task details
- `get_tasks_by_tag` - Tasks with a specific tag

### Task Modification
- `edit_task` - Update task properties
- `edit_project` - Update project settings
- `remove_task` - Delete a task
- `remove_project` - Delete a project

### Batch Operations
- `batch_add_tasks` - Create multiple tasks at once
- `batch_complete_tasks` - Mark multiple tasks as complete

### Advanced Features
- `list_custom_perspectives` - Get all perspectives
- `get_custom_perspective_tasks` - Fetch perspective tasks
- `filter_tasks` - Advanced task filtering

### Metadata & Export
- `list_projects` - Get all projects
- `list_tags` - Get all tags
- `dump_database` - Export full database as JSON

## Example Usage

### Create a Task
```python
add_task(
    name="Review quarterly report",
    project="Work",
    tags=["urgent", "review"],
    due_date="tomorrow",
    flagged=True,
    note="Check financial sections carefully"
)
```

### Query Tasks
```python
# Get flagged tasks
flagged = get_flagged_tasks()

# Filter tasks
filtered = filter_tasks(
    project_name="Work",
    is_flagged=True,
    has_due_date=True,
    search_text="report"
)
```

### Batch Operations
```python
# Create multiple tasks
batch_add_tasks([
    {"name": "Task 1", "project": "Home"},
    {"name": "Task 2", "tags": ["urgent"], "flagged": True},
    {"name": "Task 3", "due_date": "2d"}
])
```

## Architecture

The server uses:
- **FastMCP**: Simplified MCP server framework
- **OmniJS**: OmniFocus automation scripting
- **JXA**: JavaScript for Automation to bridge Python and OmniFocus
- **subprocess**: Execute AppleScript/JXA from Python

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
```

### Type Checking
```bash
mypy src/
```

## Troubleshooting

1. **Permission Issues**: Ensure Terminal/your IDE has automation permissions for OmniFocus in System Preferences > Privacy & Security > Automation

2. **OmniFocus Not Found**: Make sure OmniFocus is installed and has been opened at least once

3. **Script Errors**: Check that OmniFocus is not in a modal dialog or special state

## License

MIT

## Contributing

Contributions welcome! Please follow Python best practices and include tests for new features.

## Related

- [TypeScript Version](../): Original TypeScript implementation
- [OmniFocus Automation](https://omni-automation.com/omnifocus/): Official OmniJS documentation