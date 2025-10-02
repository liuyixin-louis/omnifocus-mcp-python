#!/usr/bin/env python3
"""
OmniFocus MCP Server
A Python-based MCP server for managing OmniFocus tasks via OmniJS.
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

mcp = FastMCP("omnifocus-mcp", "A comprehensive MCP server for managing OmniFocus tasks")


def run_omnifocus_omnijs(omnijs_code: str) -> Any:
    """
    Executes an OmniJS script in OmniFocus via AppleScript and returns the result.
    
    Args:
        omnijs_code: The OmniJS code to execute in OmniFocus.
        
    Returns:
        The parsed result from the OmniJS script execution.
        
    Raises:
        RuntimeError: If the script execution fails.
    """
    try:
        # Use JXA (JavaScript for Automation) to run OmniJS in OmniFocus
        # Escape backticks in the OmniJS code
        escaped_code = omnijs_code.replace('`', '\\`')
        jxa_wrapper = f"""
        const app = Application('OmniFocus');
        const result = app.evaluateJavascript(`{escaped_code}`);
        JSON.stringify(result);
        """
        
        proc = subprocess.run(
            ["/usr/bin/osascript", "-l", "JavaScript"],
            input=jxa_wrapper,
            capture_output=True,
            text=True,
            check=True,
        )
        
        # Parse the JSON output
        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout.strip())
            except json.JSONDecodeError:
                return proc.stdout.strip()
        return None
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        raise RuntimeError(f"OmniJS execution failed: {error_msg}")


# ===================== Task Creation Tools =====================

@mcp.tool()
def add_task(
    name: str,
    note: Optional[str] = None,
    project: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    defer_date: Optional[str] = None,
    flagged: bool = False,
    context: Optional[str] = None,
) -> str:
    """
    Adds a new task to OmniFocus using flexible transport text parsing.
    
    Args:
        name: The name of the task (required).
        note: Optional note/description for the task.
        project: Project to assign the task to (e.g., "Work" or "Work : Meetings").
        tags: List of tag names to assign to the task.
        due_date: Due date (e.g., "2d", "tomorrow", "2024-12-31", "next friday").
        defer_date: Defer date (same format as due_date).
        flagged: Whether to flag the task.
        context: Legacy context (converted to tag).
    
    Returns:
        Success message with the created task ID.
    """
    # Build transport text
    parts = [name]
    
    if project:
        parts.append(f"::{project}")
    
    if tags:
        for tag in tags:
            parts.append(f"@{tag}")
    
    # Add legacy context as a tag
    if context:
        parts.append(f"@{context}")
    
    if defer_date:
        parts.append(f"#{defer_date}")
    
    if due_date:
        parts.append(f"#{due_date}")
    
    if flagged:
        parts.append("!")
    
    transport_text = " ".join(parts).replace("'", "\\'")
    note_json = json.dumps(note if note else "")
    
    js_code = f"""
    (() => {{
        try {{
            const tasks = Task.byParsingTransportText('{transport_text}');
            if (!tasks || tasks.length === 0) {{
                return {{ error: "Failed to create task from transport text" }};
            }}
            const task = tasks[0];
            if ({note_json} !== "") {{
                task.note = {note_json};
            }}
            return {{
                success: true,
                id: task.id.primaryKey,
                name: task.name
            }};
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to create task: {result['error']}")
    
    return f"Created task '{name}' with ID: {result.get('id', 'unknown')}"


@mcp.tool()
def add_project(
    name: str,
    folder: Optional[str] = None,
    sequential: bool = False,
    review_interval: Optional[str] = None,
    completion_rule: Optional[str] = None,
) -> str:
    """
    Creates a new project in OmniFocus.
    
    Args:
        name: Name of the project.
        folder: Parent folder name (if nested).
        sequential: Whether tasks must be completed in order.
        review_interval: Review frequency (e.g., "1 week", "2 days").
        completion_rule: "last-action" or "all-actions" (default).
    
    Returns:
        Success message with the created project ID.
    """
    name_escaped = name.replace("'", "\\'")
    folder_escaped = folder.replace("'", "\\'") if folder else ""
    
    js_code = f"""
    (() => {{
        try {{
            let parent = null;
            if ('{folder_escaped}') {{
                parent = folders.byName['{folder_escaped}'] || new Folder('{folder_escaped}');
            }}
            
            const project = new Project('{name_escaped}', parent);
            
            if ({json.dumps(sequential)}) {{
                project.sequential = true;
            }}
            
            if ('{review_interval or ""}') {{
                // Parse review interval (simplified)
                const interval = '{review_interval}';
                if (interval.includes('week')) {{
                    const weeks = parseInt(interval) || 1;
                    project.reviewInterval = weeks * 7 * 24 * 60 * 60;
                }} else if (interval.includes('day')) {{
                    const days = parseInt(interval) || 1;
                    project.reviewInterval = days * 24 * 60 * 60;
                }}
            }}
            
            if ('{completion_rule or ""}' === 'last-action') {{
                project.completedByChildren = true;
            }}
            
            return {{
                success: true,
                id: project.id.primaryKey,
                name: project.name
            }};
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to create project: {result['error']}")
    
    return f"Created project '{name}' with ID: {result.get('id', 'unknown')}"


# ===================== Task Query Tools =====================

@mcp.tool()
def get_inbox_tasks() -> List[Dict[str, Any]]:
    """
    Returns all tasks in the OmniFocus inbox.
    
    Returns:
        List of task dictionaries with id, name, note, and flagged status.
    """
    js_code = """
    (() => {
        try {
            const inboxTasks = inbox.flattenedTasks || inbox.tasks || [];
            return inboxTasks.map(t => ({
                id: t.id.primaryKey,
                name: t.name,
                note: t.note || "",
                flagged: t.flagged,
                completed: t.completed
            }));
        } catch (err) {
            return { error: err.toString() };
        }
    })()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to get inbox tasks: {result['error']}")
    
    return result if isinstance(result, list) else []


@mcp.tool()
def get_flagged_tasks() -> List[Dict[str, Any]]:
    """
    Returns all flagged tasks that are not completed.
    
    Returns:
        List of flagged task dictionaries.
    """
    js_code = """
    (() => {
        try {
            return flattenedTasks.filter(t => t.flagged && !t.completed).map(t => ({
                id: t.id.primaryKey,
                name: t.name,
                project: t.containingProject ? t.containingProject.name : null,
                due: t.effectiveDueDate ? t.effectiveDueDate.toISOString() : null,
                defer: t.effectiveDeferDate ? t.effectiveDeferDate.toISOString() : null,
                note: t.note || ""
            }));
        } catch (err) {
            return { error: err.toString() };
        }
    })()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to get flagged tasks: {result['error']}")
    
    return result if isinstance(result, list) else []


@mcp.tool()
def get_forecast_tasks() -> List[Dict[str, Any]]:
    """
    Returns tasks in the forecast view (due soon or flagged).
    
    Returns:
        List of forecast task dictionaries.
    """
    js_code = """
    (() => {
        try {
            const today = new Date();
            const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
            
            return flattenedTasks.filter(t => {
                if (t.completed) return false;
                if (t.flagged) return true;
                if (t.effectiveDueDate) {
                    return t.effectiveDueDate <= weekFromNow;
                }
                return false;
            }).map(t => ({
                id: t.id.primaryKey,
                name: t.name,
                project: t.containingProject ? t.containingProject.name : null,
                due: t.effectiveDueDate ? t.effectiveDueDate.toISOString() : null,
                flagged: t.flagged,
                type: t.flagged ? "flagged" : "due"
            }));
        } catch (err) {
            return { error: err.toString() };
        }
    })()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to get forecast tasks: {result['error']}")
    
    return result if isinstance(result, list) else []


@mcp.tool()
def get_task_by_id(task_id: str) -> Dict[str, Any]:
    """
    Fetches a specific task by its ID.
    
    Args:
        task_id: The OmniFocus task ID.
        
    Returns:
        Task dictionary with full details.
    """
    task_id_escaped = task_id.replace("'", "\\'")
    
    js_code = f"""
    (() => {{
        try {{
            const task = Task.byIdentifier('{task_id_escaped}');
            if (!task) {{
                return {{ error: "Task not found" }};
            }}
            
            return {{
                id: task.id.primaryKey,
                name: task.name,
                note: task.note || "",
                completed: task.completed,
                flagged: task.flagged,
                project: task.containingProject ? task.containingProject.name : null,
                tags: task.tags.map(t => t.name),
                due: task.dueDate ? task.dueDate.toISOString() : null,
                defer: task.deferDate ? task.deferDate.toISOString() : null,
                estimated_minutes: task.estimatedMinutes,
                completion_date: task.completionDate ? task.completionDate.toISOString() : null
            }};
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to get task: {result['error']}")
    
    # Ensure we return a dict as declared
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected result type: {type(result)}")
    
    return result


@mcp.tool()
def get_tasks_by_tag(tag_name: str) -> List[Dict[str, Any]]:
    """
    Returns all tasks with a specific tag.
    
    Args:
        tag_name: Name of the tag to search for.
        
    Returns:
        List of task dictionaries with the specified tag.
    """
    tag_escaped = tag_name.replace("'", "\\'")
    
    js_code = f"""
    (() => {{
        try {{
            const tag = tags.byName['{tag_escaped}'];
            if (!tag) {{
                return [];
            }}
            
            return tag.tasks.filter(t => !t.completed).map(t => ({{
                id: t.id.primaryKey,
                name: t.name,
                project: t.containingProject ? t.containingProject.name : null,
                due: t.effectiveDueDate ? t.effectiveDueDate.toISOString() : null,
                flagged: t.flagged,
                note: t.note || ""
            }}));
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to get tasks by tag: {result['error']}")
    
    return result if isinstance(result, list) else []


@mcp.tool()
def get_completed_today() -> List[Dict[str, Any]]:
    """
    Returns tasks completed today.
    
    Returns:
        List of task dictionaries completed today.
    """
    js_code = """
    (() => {
        try {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            return flattenedTasks.filter(t => {
                return t.completed && 
                       t.completionDate >= today && 
                       t.completionDate < tomorrow;
            }).map(t => ({
                id: t.id.primaryKey,
                name: t.name,
                project: t.containingProject ? t.containingProject.name : null,
                completion_time: t.completionDate.toISOString(),
                tags: t.tags.map(tag => tag.name)
            }));
        } catch (err) {
            return { error: err.toString() };
        }
    })()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to get completed tasks: {result['error']}")
    
    return result if isinstance(result, list) else []


# ===================== Task Editing Tools =====================

@mcp.tool()
def edit_task(
    task_id: str,
    name: Optional[str] = None,
    note: Optional[str] = None,
    due_date: Optional[str] = None,
    defer_date: Optional[str] = None,
    flagged: Optional[bool] = None,
    completed: Optional[bool] = None,
    project: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """
    Edits properties of an existing task.
    
    Args:
        task_id: The OmniFocus task ID.
        name: New task name.
        note: New note/description.
        due_date: New due date (e.g., "2d", "tomorrow", "2024-12-31", null to clear).
        defer_date: New defer date (same format).
        flagged: New flagged status.
        completed: Mark task as completed/incomplete.
        project: Move task to a different project.
        tags: Replace tags (provide full list).
        
    Returns:
        Success message.
    """
    task_id_escaped = task_id.replace("'", "\\'")
    updates = []
    
    if name is not None:
        updates.append(f"task.name = {json.dumps(name)};")
    
    if note is not None:
        updates.append(f"task.note = {json.dumps(note)};")
    
    if flagged is not None:
        updates.append(f"task.flagged = {json.dumps(flagged)};")
    
    if completed is not None:
        updates.append(f"task.completed = {json.dumps(completed)};")
    
    if due_date is not None:
        if due_date:
            due_date_escaped = due_date.replace("'", "\\'")
            updates.append(f"""
                const dueStr = '{due_date_escaped}';
                if (dueStr === 'null' || dueStr === '') {{
                    task.dueDate = null;
                }} else {{
                    // Try to parse the date using various formats
                    const parsed = new Date(dueStr);
                    if (!isNaN(parsed)) {{
                        task.dueDate = parsed;
                    }} else {{
                        // Handle relative dates like "2d", "tomorrow"
                        // This would require more complex parsing
                        task.dueDate = null;
                    }}
                }}
            """)
        else:
            updates.append("task.dueDate = null;")
    
    if defer_date is not None:
        if defer_date:
            defer_date_escaped = defer_date.replace("'", "\\'")
            updates.append(f"""
                const deferStr = '{defer_date_escaped}';
                if (deferStr === 'null' || deferStr === '') {{
                    task.deferDate = null;
                }} else {{
                    const parsed = new Date(deferStr);
                    if (!isNaN(parsed)) {{
                        task.deferDate = parsed;
                    }} else {{
                        task.deferDate = null;
                    }}
                }}
            """)
        else:
            updates.append("task.deferDate = null;")
    
    if project is not None:
        project_escaped = project.replace("'", "\\'") if project else ""
        updates.append(f"""
            if ('{project_escaped}') {{
                const proj = projects.byName['{project_escaped}'];
                if (proj) {{
                    task.containingProject = proj;
                }}
            }} else {{
                task.containingProject = null;
            }}
        """)
    
    if tags is not None:
        tags_json = json.dumps(tags if tags else [])
        updates.append(f"""
            const tagNames = {tags_json};
            const newTags = [];
            tagNames.forEach(name => {{
                let tag = tags.byName[name];
                if (!tag) {{
                    tag = new Tag(name);
                }}
                newTags.push(tag);
            }});
            task.tags = newTags;
        """)
    
    if not updates:
        return "No updates specified"
    
    js_code = f"""
    (() => {{
        try {{
            const task = Task.byIdentifier('{task_id_escaped}');
            if (!task) {{
                return {{ error: "Task not found" }};
            }}
            
            {' '.join(updates)}
            
            return {{
                success: true,
                id: task.id.primaryKey,
                name: task.name
            }};
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to edit task: {result['error']}")
    
    return f"Successfully updated task: {result.get('name', 'unknown')}"


@mcp.tool()
def edit_project(
    project_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    review_interval: Optional[str] = None,
    sequential: Optional[bool] = None,
    completion_rule: Optional[str] = None,
) -> str:
    """
    Edits properties of an existing project.
    
    Args:
        project_id: The OmniFocus project ID.
        name: New project name.
        status: "active", "on-hold", "dropped", or "done".
        review_interval: Review frequency (e.g., "1 week").
        sequential: Whether tasks are sequential.
        completion_rule: "last-action" or "all-actions".
        
    Returns:
        Success message.
    """
    project_id_escaped = project_id.replace("'", "\\'")
    updates = []
    
    if name is not None:
        updates.append(f"project.name = {json.dumps(name)};")
    
    if status is not None:
        status_map = {
            "active": "Project.Status.Active",
            "on-hold": "Project.Status.OnHold",
            "dropped": "Project.Status.Dropped",
            "done": "Project.Status.Done"
        }
        if status.lower() in status_map:
            updates.append(f"project.status = {status_map[status.lower()]};")
    
    if sequential is not None:
        updates.append(f"project.sequential = {json.dumps(sequential)};")
    
    if completion_rule is not None:
        if completion_rule == "last-action":
            updates.append("project.completedByChildren = true;")
        else:
            updates.append("project.completedByChildren = false;")
    
    if review_interval is not None:
        review_interval_escaped = review_interval.replace("'", "\\'")
        updates.append(f"""
            const interval = '{review_interval_escaped}';
            if (interval.includes('week')) {{
                const weeks = parseInt(interval) || 1;
                project.reviewInterval = weeks * 7 * 24 * 60 * 60;
            }} else if (interval.includes('day')) {{
                const days = parseInt(interval) || 1;
                project.reviewInterval = days * 24 * 60 * 60;
            }} else if (interval.includes('month')) {{
                const months = parseInt(interval) || 1;
                project.reviewInterval = months * 30 * 24 * 60 * 60;
            }}
        """)
    
    if not updates:
        return "No updates specified"
    
    js_code = f"""
    (() => {{
        try {{
            const project = Project.byIdentifier('{project_id_escaped}');
            if (!project) {{
                return {{ error: "Project not found" }};
            }}
            
            {' '.join(updates)}
            
            return {{
                success: true,
                id: project.id.primaryKey,
                name: project.name
            }};
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to edit project: {result['error']}")
    
    return f"Successfully updated project: {result.get('name', 'unknown')}"


# ===================== Task Removal Tools =====================

@mcp.tool()
def remove_task(task_id: str) -> str:
    """
    Removes a task from OmniFocus.
    
    Args:
        task_id: The OmniFocus task ID.
        
    Returns:
        Success message.
    """
    task_id_escaped = task_id.replace("'", "\\'")
    
    js_code = f"""
    (() => {{
        try {{
            const task = Task.byIdentifier('{task_id_escaped}');
            if (!task) {{
                return {{ error: "Task not found" }};
            }}
            
            const name = task.name;
            deleteObject(task);
            
            return {{
                success: true,
                name: name
            }};
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to remove task: {result['error']}")
    
    return f"Successfully removed task: {result.get('name', 'unknown')}"


@mcp.tool()
def remove_project(project_id: str) -> str:
    """
    Removes a project from OmniFocus.
    
    Args:
        project_id: The OmniFocus project ID.
        
    Returns:
        Success message.
    """
    project_id_escaped = project_id.replace("'", "\\'")
    
    js_code = f"""
    (() => {{
        try {{
            const project = Project.byIdentifier('{project_id_escaped}');
            if (!project) {{
                return {{ error: "Project not found" }};
            }}
            
            const name = project.name;
            deleteObject(project);
            
            return {{
                success: true,
                name: name
            }};
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to remove project: {result['error']}")
    
    return f"Successfully removed project: {result.get('name', 'unknown')}"


# ===================== Batch Operations =====================

@mcp.tool()
def batch_add_tasks(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Adds multiple tasks in a single operation.
    
    Args:
        tasks: List of task dictionaries with same parameters as add_task.
        
    Returns:
        Dictionary with success count and list of created task IDs.
    """
    js_code = """
    (() => {
        const results = [];
        const tasksData = """ + json.dumps(tasks) + """;
        
        tasksData.forEach(taskData => {
            try {
                // Build transport text for each task
                let parts = [taskData.name];
                
                if (taskData.project) parts.push(`::${taskData.project}`);
                if (taskData.tags) {
                    taskData.tags.forEach(tag => parts.push(`@${tag}`));
                }
                if (taskData.defer_date) parts.push(`#${taskData.defer_date}`);
                if (taskData.due_date) parts.push(`#${taskData.due_date}`);
                if (taskData.flagged) parts.push("!");
                
                const transportText = parts.join(" ");
                const tasks = Task.byParsingTransportText(transportText);
                
                if (tasks && tasks.length > 0) {
                    const task = tasks[0];
                    if (taskData.note) {
                        task.note = taskData.note;
                    }
                    results.push({
                        success: true,
                        id: task.id.primaryKey,
                        name: task.name
                    });
                } else {
                    results.push({
                        success: false,
                        error: "Failed to create task",
                        name: taskData.name
                    });
                }
            } catch (err) {
                results.push({
                    success: false,
                    error: err.toString(),
                    name: taskData.name
                });
            }
        });
        
        return results;
    })()
    """
    
    result = run_omnifocus_omnijs(js_code)
    
    successful = [r for r in result if r.get("success")]
    failed = [r for r in result if not r.get("success")]
    
    return {
        "total": len(tasks),
        "successful": len(successful),
        "failed": len(failed),
        "created_ids": [r["id"] for r in successful],
        "errors": [{"name": r["name"], "error": r.get("error", "Unknown error")} for r in failed]
    }


@mcp.tool()
def batch_complete_tasks(task_ids: List[str]) -> Dict[str, Any]:
    """
    Marks multiple tasks as completed.
    
    Args:
        task_ids: List of task IDs to complete.
        
    Returns:
        Dictionary with completion statistics.
    """
    js_code = f"""
    (() => {{
        const taskIds = {json.dumps(task_ids)};
        const results = [];
        
        taskIds.forEach(id => {{
            try {{
                const task = Task.byIdentifier(id);
                if (task) {{
                    task.completed = true;
                    results.push({{
                        success: true,
                        id: id,
                        name: task.name
                    }});
                }} else {{
                    results.push({{
                        success: false,
                        id: id,
                        error: "Task not found"
                    }});
                }}
            }} catch (err) {{
                results.push({{
                    success: false,
                    id: id,
                    error: err.toString()
                }});
            }}
        }});
        
        return results;
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    
    successful = [r for r in result if r.get("success")]
    failed = [r for r in result if not r.get("success")]
    
    return {
        "total": len(task_ids),
        "completed": len(successful),
        "failed": len(failed),
        "completed_tasks": [{"id": r["id"], "name": r["name"]} for r in successful],
        "errors": [{"id": r["id"], "error": r.get("error", "Unknown error")} for r in failed]
    }


# ===================== Advanced Features =====================

@mcp.tool()
def list_custom_perspectives() -> List[Dict[str, Any]]:
    """
    Lists all available custom perspectives in OmniFocus.
    
    Returns:
        List of perspective dictionaries with id and name.
    """
    js_code = """
    (() => {
        try {
            return perspectives.map(p => ({
                id: p.id.primaryKey,
                name: p.name,
                isBuiltIn: p.isBuiltIn
            }));
        } catch (err) {
            return { error: err.toString() };
        }
    })()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to list perspectives: {result['error']}")
    
    return result if isinstance(result, list) else []


@mcp.tool()
def get_custom_perspective_tasks(perspective_name: str) -> List[Dict[str, Any]]:
    """
    Fetches tasks from a named custom perspective.
    
    Args:
        perspective_name: Name of the perspective.
        
    Returns:
        List of task dictionaries from the perspective.
    """
    perspective_escaped = perspective_name.replace("'", "\\'")
    
    # This is a simplified version - the full implementation would need
    # to parse and apply all perspective rules
    js_code = f"""
    (() => {{
        try {{
            const p = perspectives.byName['{perspective_escaped}'];
            if (!p) {{
                return {{ error: "Perspective not found" }};
            }}
            
            // Note: This is a simplified approach
            // A full implementation would need to replicate all perspective rules
            const window = document.windows[0];
            window.perspective = p;
            
            // Get visible tasks from the content tree
            const tree = window.content;
            const tasks = [];
            
            function extractTasks(items) {{
                items.forEach(item => {{
                    if (item.object instanceof Task) {{
                        tasks.push({{
                            id: item.object.id.primaryKey,
                            name: item.object.name,
                            project: item.object.containingProject ? 
                                     item.object.containingProject.name : null,
                            due: item.object.effectiveDueDate ? 
                                 item.object.effectiveDueDate.toISOString() : null,
                            flagged: item.object.flagged
                        }});
                    }}
                    if (item.children) {{
                        extractTasks(item.children);
                    }}
                }});
            }}
            
            if (tree && tree.rootNode && tree.rootNode.children) {{
                extractTasks(tree.rootNode.children);
            }}
            
            return tasks;
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to get perspective tasks: {result['error']}")
    
    return result if isinstance(result, list) else []


@mcp.tool()
def filter_tasks(
    include_completed: bool = False,
    project_name: Optional[str] = None,
    has_due_date: Optional[bool] = None,
    is_flagged: Optional[bool] = None,
    tag_names: Optional[List[str]] = None,
    search_text: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filters tasks based on various criteria.
    
    Args:
        include_completed: Include completed tasks in results.
        project_name: Filter by project name.
        has_due_date: Filter for tasks with/without due dates.
        is_flagged: Filter for flagged/unflagged tasks.
        tag_names: Filter by tags (task must have all specified tags).
        search_text: Search in task names and notes.
        
    Returns:
        List of filtered task dictionaries.
    """
    filters = []
    
    if not include_completed:
        filters.append("!t.completed")
    
    if project_name:
        project_escaped = project_name.replace("'", "\\'")
        filters.append(f"t.containingProject && t.containingProject.name === '{project_escaped}'")
    
    if has_due_date is not None:
        if has_due_date:
            filters.append("t.effectiveDueDate !== null")
        else:
            filters.append("t.effectiveDueDate === null")
    
    if is_flagged is not None:
        filters.append(f"t.flagged === {json.dumps(is_flagged)}")
    
    if tag_names:
        tag_conditions = []
        for tag in tag_names:
            tag_escaped = tag.replace("'", "\\'")
            tag_conditions.append(f"t.tags.some(tag => tag.name === '{tag_escaped}')")
        tag_check = " && ".join(tag_conditions)
        filters.append(f"({tag_check})")
    
    if search_text:
        search_escaped = search_text.replace("'", "\\'").lower()
        filters.append(
            f"(t.name.toLowerCase().includes('{search_escaped}') || " +
            f"(t.note && t.note.toLowerCase().includes('{search_escaped}')))"
        )
    
    filter_expression = " && ".join(filters) if filters else "true"
    
    js_code = f"""
    (() => {{
        try {{
            return flattenedTasks.filter(t => {filter_expression}).map(t => ({{
                id: t.id.primaryKey,
                name: t.name,
                note: t.note || "",
                completed: t.completed,
                flagged: t.flagged,
                project: t.containingProject ? t.containingProject.name : null,
                tags: t.tags.map(tag => tag.name),
                due: t.effectiveDueDate ? t.effectiveDueDate.toISOString() : null,
                defer: t.effectiveDeferDate ? t.effectiveDeferDate.toISOString() : null
            }}));
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to filter tasks: {result['error']}")
    
    return result if isinstance(result, list) else []


# ===================== Metadata & Export Tools =====================

@mcp.tool()
def list_projects() -> List[Dict[str, Any]]:
    """
    Lists all projects in OmniFocus.
    
    Returns:
        List of project dictionaries.
    """
    js_code = """
    (() => {
        try {
            return projects.map(p => {
                let statusName = 'Active';
                if (p.status) {
                    if (p.status === Project.Status.Active) statusName = 'Active';
                    else if (p.status === Project.Status.OnHold) statusName = 'OnHold';
                    else if (p.status === Project.Status.Dropped) statusName = 'Dropped';
                    else if (p.status === Project.Status.Done) statusName = 'Done';
                }
                return {
                    id: p.id.primaryKey,
                    name: p.name,
                    status: statusName,
                    folder: p.folder ? p.folder.name : null,
                    sequential: p.sequential,
                    task_count: p.tasks.length,
                    remaining_count: p.tasks.filter(t => !t.completed).length,
                    review_interval_days: p.reviewInterval ? p.reviewInterval / (24 * 60 * 60) : null
                };
            });
        } catch (err) {
            return { error: err.toString() };
        }
    })()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to list projects: {result['error']}")
    
    return result if isinstance(result, list) else []


@mcp.tool()
def list_tags() -> List[Dict[str, Any]]:
    """
    Lists all tags in OmniFocus.
    
    Returns:
        List of tag dictionaries.
    """
    js_code = """
    (() => {
        try {
            return tags.map(t => ({
                id: t.id.primaryKey,
                name: t.name,
                parent: t.parent ? t.parent.name : null,
                task_count: t.tasks.length,
                remaining_count: t.tasks.filter(task => !task.completed).length
            }));
        } catch (err) {
            return { error: err.toString() };
        }
    })()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to list tags: {result['error']}")
    
    return result if isinstance(result, list) else []


@mcp.tool()
def dump_database(
    include_completed: bool = False,
    max_depth: int = 3
) -> Dict[str, Any]:
    """
    Exports a structured dump of the OmniFocus database.
    
    Args:
        include_completed: Include completed items.
        max_depth: Maximum nesting depth for task hierarchies.
        
    Returns:
        Dictionary containing projects, tags, and inbox tasks.
    """
    js_code = f"""
    (() => {{
        try {{
            const includeCompleted = {json.dumps(include_completed)};
            const maxDepth = {max_depth};
            
            function mapTask(task, depth = 0) {{
                if (depth >= maxDepth) return null;
                if (!includeCompleted && task.completed) return null;
                
                const children = task.children
                    .map(child => mapTask(child, depth + 1))
                    .filter(c => c !== null);
                
                return {{
                    id: task.id.primaryKey,
                    name: task.name,
                    completed: task.completed,
                    flagged: task.flagged,
                    note: task.note || "",
                    tags: task.tags.map(t => t.name),
                    due: task.dueDate ? task.dueDate.toISOString() : null,
                    defer: task.deferDate ? task.deferDate.toISOString() : null,
                    children: children
                }};
            }}
            
            const projectsData = projects.map(p => {{
                const tasks = p.rootTask.children
                    .map(t => mapTask(t, 0))
                    .filter(t => t !== null);
                
                return {{
                    id: p.id.primaryKey,
                    name: p.name,
                    status: p.status.name,
                    sequential: p.sequential,
                    folder: p.folder ? p.folder.name : null,
                    tasks: tasks
                }};
            }});
            
            const tagsData = tags.map(t => ({{
                id: t.id.primaryKey,
                name: t.name,
                parent: t.parent ? t.parent.name : null
            }}));
            
            const inboxData = inbox.tasks
                .map(t => mapTask(t, 0))
                .filter(t => t !== null);
            
            return {{
                projects: projectsData,
                tags: tagsData,
                inbox: inboxData,
                stats: {{
                    total_projects: projects.length,
                    active_projects: projects.filter(p => p.status === Project.Status.Active).length,
                    total_tasks: flattenedTasks.length,
                    remaining_tasks: flattenedTasks.filter(t => !t.completed).length,
                    flagged_tasks: flattenedTasks.filter(t => !t.completed && t.flagged).length
                }}
            }};
        }} catch (err) {{
            return {{ error: err.toString() }};
        }}
    }})()
    """
    
    result = run_omnifocus_omnijs(js_code)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"Failed to dump database: {result['error']}")
    
    # Ensure we return a dict as declared
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected result type: {type(result)}")
    
    return result


# ===================== Main Entry Point =====================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()