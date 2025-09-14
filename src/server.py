#!/usr/bin/env python3
import os
from typing import Dict
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

mcp = FastMCP("Poke Lists MCP Server")

# In-memory storage for user lists (in production, use a proper database)
# Structure: {user_id: {list_name: list_data}}
user_lists_data: Dict[str, Dict[str, Dict]] = {}

def get_user_id() -> str:
    """Get user ID from x-user-id header, return 'anonymous' if not provided."""
    headers = get_http_headers()
    return headers.get("x-user-id", "anonymous")

def get_user_lists(user_id: str) -> Dict[str, Dict]:
    """Get or create user's lists storage."""
    if user_id not in user_lists_data:
        user_lists_data[user_id] = {}
    return user_lists_data[user_id]

@mcp.tool(description="Create a new list with a given name")
def create_list(name: str, description: str = "") -> dict:
    """Create a new list with the specified name and optional description."""
    user_id = get_user_id()
    user_lists = get_user_lists(user_id)
    
    if name in user_lists:
        return {"success": False, "message": f"List '{name}' already exists"}
    
    user_lists[name] = {
        "name": name,
        "description": description,
        "items": []
    }
    
    return {
        "success": True, 
        "message": f"List '{name}' created successfully",
        "list": user_lists[name]
    }

@mcp.tool(description="Add an item to a specific list")
def add_item_to_list(list_name: str, item: str, quantity: int = 1, notes: str = "") -> dict:
    """Add an item to the specified list with optional quantity and notes."""
    user_id = get_user_id()
    user_lists = get_user_lists(user_id)
    
    if list_name not in user_lists:
        return {"success": False, "message": f"List '{list_name}' does not exist"}
    
    new_item = {
        "text": item,
        "quantity": quantity,
        "notes": notes,
        "completed": False,
        "id": len(user_lists[list_name]["items"]) + 1
    }
    
    user_lists[list_name]["items"].append(new_item)
    
    return {
        "success": True,
        "message": f"Item '{item}' added to list '{list_name}'",
        "item": new_item
    }

@mcp.tool(description="Get all lists with their basic information")
def get_lists() -> dict:
    """Retrieve all lists with their names, descriptions, and item counts."""
    user_id = get_user_id()
    user_lists = get_user_lists(user_id)
    
    lists_summary = []
    for list_name, list_data in user_lists.items():
        lists_summary.append({
            "name": list_name,
            "description": list_data["description"],
            "item_count": len(list_data["items"]),
            "completed_count": sum(1 for item in list_data["items"] if item["completed"])
        })
    
    return {
        "success": True,
        "lists": lists_summary,
        "total_lists": len(lists_summary)
    }

@mcp.tool(description="Get all items from a specific list")
def get_list_items(list_name: str) -> dict:
    """Retrieve all items from the specified list."""
    user_id = get_user_id()
    user_lists = get_user_lists(user_id)
    
    if list_name not in user_lists:
        return {"success": False, "message": f"List '{list_name}' does not exist"}
    
    return {
        "success": True,
        "list_name": list_name,
        "items": user_lists[list_name]["items"],
        "total_items": len(user_lists[list_name]["items"])
    }

@mcp.tool(description="Remove an item from a specific list")
def remove_item_from_list(list_name: str, item_id: int) -> dict:
    """Remove an item from the specified list by its ID."""
    user_id = get_user_id()
    user_lists = get_user_lists(user_id)
    
    if list_name not in user_lists:
        return {"success": False, "message": f"List '{list_name}' does not exist"}
    
    items = user_lists[list_name]["items"]
    item_to_remove = None
    
    for i, item in enumerate(items):
        if item["id"] == item_id:
            item_to_remove = items.pop(i)
            break
    
    if item_to_remove:
        return {
            "success": True,
            "message": f"Item removed from list '{list_name}'",
            "removed_item": item_to_remove
        }
    else:
        return {"success": False, "message": f"Item with ID {item_id} not found in list '{list_name}'"}

@mcp.tool(description="Delete an entire list")
def delete_list(list_name: str) -> dict:
    """Delete the specified list and all its items."""
    user_id = get_user_id()
    user_lists = get_user_lists(user_id)
    
    if list_name not in user_lists:
        return {"success": False, "message": f"List '{list_name}' does not exist"}
    
    deleted_list = user_lists.pop(list_name)
    
    return {
        "success": True,
        "message": f"List '{list_name}' deleted successfully",
        "deleted_list": deleted_list
    }

@mcp.tool(description="Mark an item as completed or uncompleted in a list")
def toggle_item_completion(list_name: str, item_id: int) -> dict:
    """Toggle the completion status of an item in the specified list."""
    user_id = get_user_id()
    user_lists = get_user_lists(user_id)
    
    if list_name not in user_lists:
        return {"success": False, "message": f"List '{list_name}' does not exist"}
    
    items = user_lists[list_name]["items"]
    
    for item in items:
        if item["id"] == item_id:
            item["completed"] = not item["completed"]
            status = "completed" if item["completed"] else "uncompleted"
            return {
                "success": True,
                "message": f"Item marked as {status}",
                "item": item
            }
    
    return {"success": False, "message": f"Item with ID {item_id} not found in list '{list_name}'"}

@mcp.tool(description="Search for items across all lists or within a specific list")
def search_items(query: str, list_name: str = None) -> dict:
    """Search for items containing the query text across all lists or within a specific list."""
    user_id = get_user_id()
    user_lists = get_user_lists(user_id)
    
    results = []
    
    lists_to_search = {list_name: user_lists[list_name]} if list_name and list_name in user_lists else user_lists
    
    for list_name, list_data in lists_to_search.items():
        for item in list_data["items"]:
            if query.lower() in item["text"].lower() or query.lower() in item["notes"].lower():
                results.append({
                    "list_name": list_name,
                    "item": item
                })
    
    return {
        "success": True,
        "query": query,
        "results": results,
        "total_found": len(results)
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting FastMCP server on {host}:{port}")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
