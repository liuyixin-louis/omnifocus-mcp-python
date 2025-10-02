# FastMCP Development Guide

A comprehensive guide to developing MCP servers using FastMCP, based on real-world implementation patterns.

## Table of Contents
1. [Overview](#overview)
2. [Basic Setup](#basic-setup)
3. [Core Patterns](#core-patterns)
4. [Tool Development](#tool-development)
5. [Error Handling](#error-handling)
6. [Type Safety](#type-safety)
7. [Testing Strategy](#testing-strategy)
8. [Deployment](#deployment)
9. [Best Practices](#best-practices)

## Overview

FastMCP is a Python framework that simplifies creating MCP (Model Context Protocol) servers. It provides decorators and utilities for exposing Python functions as tools that AI assistants can use.

### Key Benefits
- **Minimal Boilerplate**: Simple decorator-based API
- **Type Safety**: Automatic type validation with Python type hints
- **Built-in Documentation**: Docstrings become tool descriptions
- **Error Handling**: Structured error propagation
- **Fast Development**: Focus on business logic, not protocol details

## Basic Setup

### 1. Project Structure
```
your-mcp-project/
├── src/
│   └── server.py           # Main server file
├── tests/
│   └── test_server.py      # Test suite
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

### 2. Dependencies

**pyproject.toml**:
```toml
[project]
name = "your-mcp-server"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "mypy>=1.0.0",
    "black>=23.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

### 3. Server Initialization

**Basic Pattern**:
```python
#!/usr/bin/env python3
"""Your MCP Server Description."""

from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any

# Initialize with name and description
mcp = FastMCP(
    "server-name",
    "Comprehensive description of what your server does"
)

# Server will run when executed
if __name__ == "__main__":
    mcp.run()
```

## Core Patterns

### 1. Simple Tool Pattern
```python
@mcp.tool()
def get_status() -> str:
    """Get the current system status."""
    return "System is running"
```

### 2. Parameterized Tool Pattern
```python
@mcp.tool()
def process_data(
    input_text: str,
    max_length: Optional[int] = None,
    include_metadata: bool = False
) -> Dict[str, Any]:
    """
    Process input data with optional parameters.
    
    Args:
        input_text: The text to process (required)
        max_length: Maximum length of output (optional)
        include_metadata: Whether to include metadata (default: False)
    
    Returns:
        Dictionary containing processed results.
    """
    result = {"processed": input_text[:max_length] if max_length else input_text}
    
    if include_metadata:
        result["metadata"] = {
            "length": len(input_text),
            "truncated": max_length and len(input_text) > max_length
        }
    
    return result
```

### 3. External Integration Pattern
```python
def call_external_api(command: str) -> Any:
    """
    Helper function to call external services.
    Centralize external calls for better error handling.
    """
    try:
        # Your integration logic here
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr}")
    except json.JSONDecodeError:
        return result.stdout  # Fallback for non-JSON

@mcp.tool()
def execute_command(command: str) -> Dict[str, Any]:
    """Execute a system command and return results."""
    try:
        result = call_external_api(command)
        return {"success": True, "result": result}
    except RuntimeError as e:
        return {"success": False, "error": str(e)}
```

## Tool Development

### 1. CRUD Operations Pattern

```python
# CREATE
@mcp.tool()
def create_item(
    name: str,
    description: Optional[str] = None,
    **kwargs
) -> str:
    """Create a new item with flexible attributes."""
    # Implementation
    return f"Created item with ID: {item_id}"

# READ
@mcp.tool()
def get_item(item_id: str) -> Dict[str, Any]:
    """Retrieve a specific item by ID."""
    # Implementation
    return {"id": item_id, "name": "...", ...}

@mcp.tool()
def list_items(
    filter_by: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """List items with optional filtering."""
    # Implementation
    return [...]

# UPDATE
@mcp.tool()
def update_item(
    item_id: str,
    **updates
) -> str:
    """Update item properties."""
    # Only update provided fields
    return f"Updated item: {item_id}"

# DELETE
@mcp.tool()
def delete_item(item_id: str) -> str:
    """Delete an item permanently."""
    # Implementation
    return f"Deleted item: {item_id}"
```

### 2. Batch Operations Pattern

```python
@mcp.tool()
def batch_process(
    items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Process multiple items in a single operation.
    
    Args:
        items: List of item dictionaries to process
    
    Returns:
        Summary with success/failure counts and details.
    """
    results = []
    successful = []
    failed = []
    
    for item in items:
        try:
            # Process each item
            result = process_single_item(item)
            results.append({"success": True, "data": result})
            successful.append(result)
        except Exception as e:
            results.append({"success": False, "error": str(e)})
            failed.append({"item": item, "error": str(e)})
    
    return {
        "total": len(items),
        "successful": len(successful),
        "failed": len(failed),
        "results": results,
        "summary": {
            "successful_ids": [s.get("id") for s in successful],
            "errors": failed
        }
    }
```

### 3. Query/Filter Pattern

```python
@mcp.tool()
def search_items(
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Advanced search with multiple criteria.
    
    Args:
        query: Text search query
        filters: Dictionary of field:value filters
        sort_by: Field to sort by
        limit: Maximum results
        offset: Pagination offset
    
    Returns:
        Search results with pagination info.
    """
    # Build query
    all_items = get_all_items()
    filtered = all_items
    
    # Apply text search
    if query:
        filtered = [i for i in filtered if query.lower() in i["name"].lower()]
    
    # Apply filters
    if filters:
        for key, value in filters.items():
            filtered = [i for i in filtered if i.get(key) == value]
    
    # Sort
    if sort_by:
        filtered.sort(key=lambda x: x.get(sort_by, ""))
    
    # Paginate
    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    
    return {
        "items": paginated,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    }
```

## Error Handling

### 1. Graceful Degradation Pattern

```python
@mcp.tool()
def safe_operation(data: str) -> Dict[str, Any]:
    """Operation with comprehensive error handling."""
    try:
        # Primary operation
        result = perform_operation(data)
        return {"success": True, "result": result}
    
    except SpecificError as e:
        # Handle known errors
        return {"success": False, "error": str(e), "error_type": "specific"}
    
    except Exception as e:
        # Catch-all for unexpected errors
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown"
        }
```

### 2. Validation Pattern

```python
@mcp.tool()
def validated_operation(
    email: str,
    age: int,
    options: Optional[List[str]] = None
) -> str:
    """Operation with input validation."""
    # Email validation
    if not "@" in email:
        raise ValueError(f"Invalid email format: {email}")
    
    # Range validation
    if not 0 <= age <= 150:
        raise ValueError(f"Age must be between 0 and 150, got {age}")
    
    # Options validation
    valid_options = ["opt1", "opt2", "opt3"]
    if options:
        invalid = [o for o in options if o not in valid_options]
        if invalid:
            raise ValueError(f"Invalid options: {invalid}")
    
    # Proceed with operation
    return "Operation completed successfully"
```

## Type Safety

### 1. Type Hints Best Practices

```python
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime

@mcp.tool()
def typed_function(
    # Required parameters
    name: str,
    count: int,
    
    # Optional parameters
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    
    # Union types
    date: Optional[Union[str, datetime]] = None,
    
    # Literal types for enums
    status: Literal["active", "inactive", "pending"] = "active",
    
    # Complex nested types
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Function with comprehensive type hints."""
    return {
        "name": name,
        "count": count,
        "status": status,
        # ... process other parameters
    }
```

### 2. Return Type Consistency

```python
# Always return the declared type
@mcp.tool()
def get_data(item_id: str) -> Dict[str, Any]:
    """Ensure return type matches declaration."""
    result = fetch_from_database(item_id)
    
    # Type checking for mypy
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected result type: {type(result)}")
    
    return result

# For lists, ensure empty list on no results
@mcp.tool()
def list_data() -> List[Dict[str, Any]]:
    """Always return list, even if empty."""
    result = fetch_all_from_database()
    return result if isinstance(result, list) else []
```

## Testing Strategy

### 1. Test Structure

```python
#!/usr/bin/env python3
"""Test suite for MCP server."""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from server import (
    function1,
    function2,
    # ... import all functions to test
)

# Unit tests
def test_simple_function():
    """Test basic functionality."""
    result = function1("input")
    assert result == "expected"
    assert isinstance(result, str)

def test_complex_function():
    """Test with multiple assertions."""
    result = function2(param1="value", param2=123)
    
    # Structure assertions
    assert isinstance(result, dict)
    assert "key1" in result
    assert "key2" in result
    
    # Value assertions
    assert result["key1"] == "expected_value"
    assert result["key2"] > 0

# Parametrized tests
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    (None, "default"),
])
def test_parametrized(input, expected):
    """Test multiple input scenarios."""
    result = function3(input)
    assert result == expected

# Error handling tests
def test_error_handling():
    """Test error conditions."""
    with pytest.raises(ValueError):
        function4(invalid_param="bad")
    
    # Test graceful error handling
    result = safe_function(bad_input="test")
    assert result["success"] is False
    assert "error" in result
```

### 2. Integration Test Pattern

```python
def test_integration_workflow():
    """Test complete workflow."""
    # Create
    create_result = create_item("Test Item")
    assert "ID:" in create_result
    item_id = create_result.split("ID: ")[1]
    
    # Read
    item = get_item(item_id)
    assert item["name"] == "Test Item"
    
    # Update
    update_result = update_item(item_id, name="Updated Item")
    assert "Updated" in update_result
    
    # Verify update
    updated = get_item(item_id)
    assert updated["name"] == "Updated Item"
    
    # Delete
    delete_result = delete_item(item_id)
    assert "Deleted" in delete_result

# Run tests standalone
if __name__ == "__main__":
    # Can run without pytest
    test_simple_function()
    test_integration_workflow()
    print("All tests passed!")
```

## Deployment

### 1. Development Testing

```bash
# Install in development mode
pip install -e ".[dev]"

# Run with MCP dev server
mcp dev src/server.py

# Access at http://localhost:6274/
```

### 2. Claude Desktop Integration

**Config location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "your-server": {
      "command": "/usr/bin/python3",
      "args": ["/absolute/path/to/src/server.py"],
      "env": {
        "YOUR_API_KEY": "optional-api-key"
      }
    }
  }
}
```

### 3. Production Checklist

- [ ] All tests passing
- [ ] MyPy type checking clean
- [ ] Error handling for all external calls
- [ ] Documentation complete
- [ ] README with examples
- [ ] Version tagged
- [ ] Requirements pinned

## Best Practices

### 1. Function Naming
```python
# Use clear, action-oriented names
@mcp.tool()
def create_task(...) -> str: ...      # Good
def task(...) -> str: ...              # Bad - ambiguous

@mcp.tool()
def list_active_projects(...): ...     # Good
def projects(...): ...                 # Bad - unclear action
```

### 2. Documentation
```python
@mcp.tool()
def complex_operation(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """
    Brief one-line description.
    
    Detailed explanation of what this function does,
    when to use it, and any important notes.
    
    Args:
        param1: Clear description of this parameter
        param2: Optional parameter explanation (default: None)
    
    Returns:
        Dictionary containing:
        - key1: Description of this field
        - key2: Description of this field
    
    Raises:
        ValueError: When input validation fails
        RuntimeError: When external operation fails
    
    Examples:
        >>> complex_operation("test", param2=5)
        {"key1": "value", "key2": 5}
    """
    # Implementation
```

### 3. Separation of Concerns
```python
# Separate business logic from MCP decorators

# Business logic (testable)
def calculate_result(input_data: str) -> Dict[str, Any]:
    """Pure business logic function."""
    # Complex processing
    return processed_data

# MCP wrapper (thin layer)
@mcp.tool()
def process_data(input_data: str) -> Dict[str, Any]:
    """MCP tool that wraps business logic."""
    try:
        return calculate_result(input_data)
    except Exception as e:
        return {"error": str(e)}
```

### 4. Configuration Management
```python
import os
from pathlib import Path

# Configuration at module level
CONFIG = {
    "api_key": os.environ.get("API_KEY"),
    "timeout": int(os.environ.get("TIMEOUT", "30")),
    "max_retries": int(os.environ.get("MAX_RETRIES", "3")),
    "cache_dir": Path.home() / ".cache" / "mcp_server"
}

# Validate on startup
def validate_config():
    """Validate configuration on server start."""
    if not CONFIG["api_key"]:
        raise ValueError("API_KEY environment variable required")
    
    CONFIG["cache_dir"].mkdir(parents=True, exist_ok=True)

# Use in tools
@mcp.tool()
def authenticated_operation() -> str:
    """Operation using configuration."""
    headers = {"Authorization": f"Bearer {CONFIG['api_key']}"}
    # ... use configuration
```

### 5. Logging and Debugging
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@mcp.tool()
def debuggable_operation(data: str) -> Dict[str, Any]:
    """Operation with logging for debugging."""
    logger.info(f"Starting operation with data: {data[:50]}...")
    
    try:
        result = process(data)
        logger.info(f"Operation successful: {len(result)} items")
        return {"success": True, "result": result}
    
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
```

## Common Patterns Summary

1. **Always use type hints** - FastMCP leverages them for validation
2. **Write comprehensive docstrings** - They become tool descriptions
3. **Return consistent types** - Match your declared return types
4. **Handle errors gracefully** - Return error dictionaries vs raising
5. **Keep tools focused** - One tool, one purpose
6. **Centralize external calls** - Easier testing and error handling
7. **Use Optional for nullable parameters** - Clear API contract
8. **Validate inputs early** - Fail fast with clear messages
9. **Test everything** - Both unit and integration tests
10. **Document usage examples** - In docstrings and README

## Conclusion

FastMCP provides an elegant, Pythonic way to build MCP servers. By following these patterns, you can create robust, type-safe, and maintainable MCP servers that integrate seamlessly with AI assistants like Claude.

The key is to focus on your domain logic while letting FastMCP handle the protocol details. Keep your tools simple, well-documented, and thoroughly tested for the best results.