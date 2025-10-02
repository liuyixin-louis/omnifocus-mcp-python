#!/usr/bin/env python3
"""
Test script for OmniFocus MCP server.
Run this to verify the server works with your OmniFocus installation.
Can be run with pytest or directly as a script.
"""

import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from omnifocus_server import (
    run_omnifocus_omnijs,
    add_task,
    get_inbox_tasks,
    get_flagged_tasks,
    list_projects,
    list_tags,
)


def test_omnijs_execution():
    """Test basic OmniJS execution."""
    result = run_omnifocus_omnijs("(() => { return 'Hello from OmniFocus'; })()")
    assert result == 'Hello from OmniFocus', f"Expected 'Hello from OmniFocus', got {result}"
    print(f"✓ OmniJS execution works: {result}")


def test_create_task():
    """Test creating a task."""
    result = add_task(
        name="Test task from Python MCP",
        note="This is a test task created by the Python MCP server",
        flagged=True,
        due_date="tomorrow"
    )
    assert "Created task" in result, f"Task creation failed: {result}"
    assert "Test task from Python MCP" in result, f"Task name not in result: {result}"
    print(f"✓ Task created: {result}")


def test_query_inbox():
    """Test querying inbox tasks."""
    tasks = get_inbox_tasks()
    assert isinstance(tasks, list), f"Expected list, got {type(tasks)}"
    print(f"✓ Found {len(tasks)} tasks in inbox")
    if tasks:
        assert 'id' in tasks[0], "Task missing 'id' field"
        assert 'name' in tasks[0], "Task missing 'name' field"
        print(f"  First task: {tasks[0].get('name', 'Unknown')}")


def test_query_flagged():
    """Test querying flagged tasks."""
    tasks = get_flagged_tasks()
    assert isinstance(tasks, list), f"Expected list, got {type(tasks)}"
    print(f"✓ Found {len(tasks)} flagged tasks")
    if tasks:
        assert 'id' in tasks[0], "Task missing 'id' field"
        assert 'name' in tasks[0], "Task missing 'name' field"
        print(f"  First flagged task: {tasks[0].get('name', 'Unknown')}")


def test_list_projects():
    """Test listing projects."""
    projects = list_projects()
    assert isinstance(projects, list), f"Expected list, got {type(projects)}"
    print(f"✓ Found {len(projects)} projects")
    if projects:
        assert 'id' in projects[0], "Project missing 'id' field"
        assert 'name' in projects[0], "Project missing 'name' field"
        assert 'status' in projects[0], "Project missing 'status' field"
        active = [p for p in projects if p.get('status') == 'Active']
        print(f"  Active projects: {len(active)}")


def test_list_tags():
    """Test listing tags."""
    tags = list_tags()
    assert isinstance(tags, list), f"Expected list, got {type(tags)}"
    print(f"✓ Found {len(tags)} tags")
    if tags:
        assert 'id' in tags[0], "Tag missing 'id' field"
        assert 'name' in tags[0], "Tag missing 'name' field"
        print(f"  First tag: {tags[0].get('name', 'Unknown')}")


def main():
    """Run all tests when script is executed directly."""
    print("=" * 50)
    print("OmniFocus MCP Server Test Suite")
    print("=" * 50)
    
    tests = [
        test_omnijs_execution,
        test_create_task,
        test_query_inbox,
        test_query_flagged,
        test_list_projects,
        test_list_tags,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        test_name = test.__name__.replace('test_', '').replace('_', ' ').title()
        print(f"\nRunning: {test_name}")
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name} error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{passed + failed}")
    
    if failed == 0:
        print("✓ All tests passed! The server is working correctly.")
        return 0
    else:
        print(f"✗ {failed} test(s) failed. Check the output above.")
        return 1


if __name__ == "__main__":
    # Run directly or with pytest
    if 'pytest' in sys.modules:
        # Running under pytest - tests will be discovered automatically
        pass
    else:
        # Running as a script
        sys.exit(main())