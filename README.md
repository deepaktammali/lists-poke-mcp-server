# Poke Lists MCP Server

A Model Context Protocol (MCP) server that provides comprehensive list management functionality for Poke integrations. Perfect for shopping lists, todo lists, project lists, and any other list-based organization.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/InteractionCo/mcp-server-template)

## Features

- **User-specific lists** - Each user has their own isolated list storage
- **Complete CRUD operations** - Create, read, update, and delete lists and items
- **Item management** - Add items with quantity, notes, and completion status
- **Search functionality** - Search across all lists or within specific lists
- **Rich item data** - Track text, quantity, notes, completion status, and unique IDs

## API Functions

### List Management
- `create_list(name, description)` - Create a new list
- `get_lists()` - Get all lists with summaries
- `delete_list(list_name)` - Delete an entire list

### Item Management
- `add_item_to_list(list_name, item, quantity, notes)` - Add item to list
- `get_list_items(list_name)` - Get all items from a specific list
- `remove_item_from_list(list_name, item_id)` - Remove item by ID
- `toggle_item_completion(list_name, item_id)` - Mark item complete/incomplete

### Search & Discovery
- `search_items(query, list_name)` - Search items across lists

## User Authentication

The server uses the `x-user-id` header to isolate data between users. Each user's lists are completely separate and secure.

**Example Header:**
```
x-user-id: user123
```

If no `x-user-id` header is provided, the server defaults to "anonymous" user.

## Poke Integration

### Adding to Poke
1. Deploy this MCP server to your hosting platform
2. Go to https://poke.com/settings/connections/integrations/new
3. Add your server URL
4. Configure the `x-user-id` header in your Poke automation settings

### Example Poke Automation
```javascript
// Create a shopping list automation
await mcp.create_list("Weekly Shopping", "My weekly grocery list");

// Add items via email trigger
await mcp.add_item_to_list("Weekly Shopping", "Milk", 2, "Organic if available");
await mcp.add_item_to_list("Weekly Shopping", "Bread", 1, "Whole grain");

// Check off completed items
await mcp.toggle_item_completion("Weekly Shopping", 1);
```

## Local Development

### Setup

Fork the repo, then run:

```bash
git clone <your-repo-url>
cd mcp-server-template
conda create -n mcp-server python=3.13
conda activate mcp-server
pip install -r requirements.txt
```

### Test

```bash
python src/server.py
# then in another terminal run:
npx @modelcontextprotocol/inspector
```

Open http://localhost:3000 and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport (NOTE THE `/mcp`!).

## Deployment

### Option 1: One-Click Deploy
Click the "Deploy to Render" button above.

### Option 2: Manual Deployment
1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service on Render
4. Connect your forked repository
5. Render will automatically detect the `render.yaml` configuration

Your server will be available at `https://your-service-name.onrender.com/mcp` (NOTE THE `/mcp`!)

## Poke Setup

You can connect your MCP server to Poke at (poke.com/settings/connections)[poke.com/settings/connections].
To test the connection explitly, ask poke somethink like `Tell the subagent to use the "{connection name}" integration's "{tool name}" tool`.
If you run into persistent issues of poke not calling the right MCP (e.g. after you've renamed the connection) you may send `clearhistory` to poke to delete all message history and start fresh.
We're working hard on improving the integration use of Poke :)


## Production Deployment Checklist

### Database Migration
- [ ] Replace in-memory storage with persistent database (PostgreSQL/MongoDB)
- [ ] Add database connection pooling
- [ ] Implement proper data migrations
- [ ] Add database backup and recovery procedures

### Security & Authentication
- [ ] Implement proper user authentication beyond header-based
- [ ] Add JWT token validation
- [ ] Set up rate limiting per user
- [ ] Add input validation and sanitization
- [ ] Implement HTTPS/TLS encryption
- [ ] Add CORS configuration for web clients

### Data Management
- [ ] Add timestamp fields if needed (created_at, updated_at)
- [ ] Implement soft delete for lists and items
- [ ] Add data export functionality
- [ ] Set up automated data backups
- [ ] Add data retention policies

### Performance & Scalability
- [ ] Add Redis caching layer
- [ ] Implement database indexing
- [ ] Add connection pooling
- [ ] Set up load balancing
- [ ] Add database read replicas
- [ ] Implement pagination for large lists

## Customization

Add more tools by decorating functions with `@mcp.tool`:

```python
@mcp.tool
def calculate(x: float, y: float, operation: str) -> float:
    """Perform basic arithmetic operations."""
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y
    # ...
```
