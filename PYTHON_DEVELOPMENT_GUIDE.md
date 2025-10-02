# Guide: Building an OmniFocus MCP Server in Python

This document outlines how to create a Python-based MCP (Model-Context Protocol) server to interact with OmniFocus, mirroring the functionality of the existing TypeScript `omnifocus-mcp-enhanced` project.

The core principle is to use Python to execute OmniJS (Omni Automation JavaScript) via AppleScript, as demonstrated in the initial example.

## 1. Setup

First, ensure you have the MCP SDK installed in your Python environment:

```bash
# Using pip
pip install "mcp[cli]"

# Or using uv
uv venv
uv pip install "mcp[cli]"
```

## 2. Core Architecture

The server will consist of a main Python file (e.g., `omnifocus_server.py`) that defines the MCP tools. A central utility function will be responsible for running the OmniJS code.

```python
# omnifocus_server.py
from mcp.server.fastmcp import FastMCP
import subprocess
import json

mcp = FastMCP("omnifocus_tools", "A set of tools to manage OmniFocus tasks.")

def run_omnifocus_omnijs(omnijs_code: str) -> str:
    """
    Executes an OmniJS script in OmniFocus via AppleScript and returns the result.
    """
    # The -l JavaScript flag tells osascript to interpret the script as JavaScript for Automation (JXA) 
    # This is generally more robust for passing complex data than embedding in an AppleScript string.
    try:
        proc = subprocess.run(
            ["/usr/bin/osascript", "-l", "JavaScript"],
            input=f"JSON.stringify(Application('OmniFocus').evaluateJavascript(`{omnijs_code}`))",
            capture_output=True,
            text=True,
            check=True,
        )
        # The output from JXA is a JSON string (e.g., '"OK"' or '["Task 1","Task 2"]'),
        # so we parse it to get the actual value.
        return json.loads(proc.stdout.strip())
    except subprocess.CalledProcessError as e:
        # Stderr often contains useful debugging info from OmniFocus or the script itself.
        raise RuntimeError(f"OmniJS execution failed: {e.stderr.strip()}")
    except json.JSONDecodeError:
        # Fallback for scripts that might not return valid JSON
        return proc.stdout.strip()

# ... tool definitions will go here ...

if __name__ == "__main__":
    mcp.run()
```

## 3. Implementing the Tools

Here are the Python equivalents for the core features found in the TypeScript project. Each function is decorated with `@mcp.tool()` and uses the `run_omnifocus_omnijs` helper.

### Task & Project Creation

```python
@mcp.tool()
def add_task(
    name: str,
    note: str | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    defer_date: str | None = None,
    flagged: bool = False,
) -> str:
    """
    Adds a new task to OmniFocus using flexible transport text parsing.

    Args:
        name: The name of the task.
        note: An optional note for the task.
        project: The project to assign the task to.
        tags: A list of tags to assign.
        due_date: The due date in a format OmniFocus understands (e.g., '2d', 'tomorrow', '2024-12-31').
        defer_date: The defer date.
        flagged: Whether to flag the task.
    """
    parts = [name]
    if project:
        parts.append(f"::{project}")
    if tags:
        for tag in tags:
            parts.append(f"@{tag}")
    if defer_date:
        parts.append(f"#{defer_date}")  # Defer date is the first '#'
    if due_date:
        parts.append(f"#{due_date}")    # Due date is the second '#'
    if flagged:
        parts.append("!")

    transport_text = " ".join(parts)
    note_json = json.dumps(note if note else "")

    js_code = f"""
    (() => {
        const tasks = Task.byParsingTransportText('{transport_text.replace("'", "\'"')}')
        if (!tasks || tasks.length === 0) return "ERROR: Task not created."
        const task = tasks[0]
        if ({note_json} !== "") {
            task.note = {note_json};
        }
        return `OK: Created task with ID: ${{task.id.primaryKey}}`
    }})()"""
    return run_omnifocus_omnijs(js_code)

@mcp.tool()
def add_project(name: str) -> str:
    """Adds a new project to OmniFocus."""
    js_code = f"""
    new Project('{name.replace("'", "\'"')}')
    return "OK: Project created."
    """
    return run_omnifocus_omnijs(js_code)
```

### Task Querying

```python
@mcp.tool()
def get_inbox_tasks() -> list[dict]:
    """Returns a list of tasks in the OmniFocus inbox."""
    js_code = """
    inbox.tasks.map(t => ({
        id: t.id.primaryKey,
        name: t.name,
        note: t.note,
        completed: t.completed
    }));
    """
    return run_omnifocus_omnijs(js_code)

@mcp.tool()
def get_flagged_tasks() -> list[dict]:
    """Returns a list of all flagged tasks."""
    js_code = """
    flattenedTasks.filter(t => t.flagged && !t.completed).map(t => ({
        id: t.id.primaryKey,
        name: t.name,
        project: t.containingProject ? t.containingProject.name : 'None',
        due: t.effectiveDueDate
    }));
    """
    return run_omnifocus_omnijs(js_code)

@mcp.tool()
def get_forecast_tasks() -> list[dict]:
    """Returns tasks that are part of the forecast (due or flagged)."""
    js_code = """
    forecast.tasks.map(t => ({
        id: t.id.primaryKey,
        name: t.name,
        project: t.containingProject ? t.containingProject.name : 'None',
        due: t.effectiveDueDate
    }));
    """
    return run_omnifocus_omnijs(js_code)

@mcp.tool()
def get_task_by_id(task_id: str) -> dict:
    """Fetches a single task by its primary key."""
    js_code = f"""
    const task = Task.byIdentifier('{task_id}');
    if (task) {
        return {{
            id: task.id.primaryKey,
            name: task.name,
            note: task.note,
            completed: task.completed,
            project: task.containingProject ? task.containingProject.name : null,
            tags: task.tags.map(t => t.name),
            due: task.dueDate,
            defer: task.deferDate
        }};
    }} else {
        return null;
    }
    """
    return run_omnifocus_omnijs(js_code)
```

### Advanced Features

#### Listing Custom Perspectives
This is a key feature of the original repository.

```python
@mcp.tool()
def list_custom_perspectives() -> list[dict]:
    """Lists all available custom perspectives."""
    js_code = """
    perspectives.filter(p => p.status === Perspective.Status.Active).map(p => ({
        id: p.id.primaryKey,
        name: p.name
    }));
    """
    return run_omnifocus_omnijs(js_code)
```

#### Getting Tasks from a Custom Perspective
This requires running a more complex script that emulates what OmniFocus does when you open a perspective.

```python
@mcp.tool()
def get_custom_perspective_tasks(perspective_name: str) -> list[dict]:
    """
    Fetches tasks from a named custom perspective.
    Note: This is a simplified version. The original repo has a more complex
    script to handle various perspective rules.
    """
    # This OmniJS is highly complex. For a robust solution, you would need to
    # replicate the logic from 'getCustomPerspectiveTasks.js' in the original repo.
    # The script below is a placeholder showing the concept.
    js_code = f"""
    (() => {
        const p = perspectives.byName['{perspective_name.replace("'", "\'"')}'];
        if (!p) {
            return {{error: "Perspective not found."}};
        }
        # This is a simplification. Real perspective logic is much more involved.
        # It requires re-implementing the perspective's rules in JavaScript.
        # The original repo contains a script that does this.
        const taskTree = p.taskTree();
        const tasks = [];
        function processTask(task) {
            tasks.push({
                id: task.id.primaryKey,
                name: task.name,
                due: task.effectiveDueDate
            });
            task.children.forEach(processTask);
        }
        taskTree.root.children.forEach(processTask);
        return tasks;
    }})()"""
    return run_omnifocus_omnijs(js_code)
```

### Database Dump

```python
@mcp.tool()
def dump_database() -> dict:
    """
    Dumps a structured representation of the entire OmniFocus database as JSON.
    This can be a very large object.
    """
    # This script is adapted from the original repo's 'omnifocusDump.js'
    js_code = """
    (() => {
      const toJSON = (obj) => JSON.parse(JSON.stringify(obj));

      return {
        projects: projects.map(p => ({
          id: p.id.primaryKey,
          name: p.name,
          status: p.status.name,
          tasks: p.rootTask.children.map(function mapTasks(t) {
            return {
              id: t.id.primaryKey,
              name: t.name,
              completed: t.completed,
              children: t.children.map(mapTasks)
            };
          })
        })),
        tags: tags.map(t => ({ id: t.id.primaryKey, name: t.name })),
        inboxTasks: inbox.tasks.map(t => ({ id: t.id.primaryKey, name: t.name, completed: t.completed }))
      };
    })();
    """
    return run_omnifocus_omnijs(js_code)
```

## 4. Running and Testing

To test your server locally, use the `mcp dev` command, which provides a web interface to inspect and call your tools.

```bash
uv run mcp dev omnifocus_server.py
```

From there, you can invoke tools like `list_inbox_tasks` and see the output directly from OmniFocus.

This guide provides a solid foundation. For more complex features like `filterTasks` or a fully accurate `get_custom_perspective_tasks`, you will need to port the corresponding JavaScript logic from the `.js` files in the original repository's `src/utils/omnifocusScripts/` directory.
