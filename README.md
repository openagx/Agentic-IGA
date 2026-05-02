# midPoint LangGraph Agent Framework

This project provides an MCP (Model Context Protocol) server and a LangGraph-based AI agent to interact with the midPoint identity management system via its REST API.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenHands Agent                        │
│              (LangGraph + OpenHands SDK)                 │
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  Terminal  │    │   MCP     │    │  Skills   │  │
│  │   Tool    │    │  Client   │    │ (RAG)    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
└──────────────────────────┬──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   MCP       │
                    │   Server    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  midPoint   │
                    │  REST API  │
                    └───────────┘
```

## Components

### 1. MCP Server (`midpoint_mcp/`)
- Provides tools to interact with midPoint REST API
- Supports user, role, org, and resource management
- Handles search and RPC operations

### 2. Agent (`midpoint_agent/`)
- Built with OpenHands SDK (LangGraph)
- File-based sub-agent definition
- midPoint domain skill for context

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `MIDPOINT_URL` - Your midPoint instance URL
- `MIDPOINT_USERNAME` - Username
- `MIDPOINT_PASSWORD` - Password
- `LLM_API_KEY` - Your LLM API key

### 3. Run the MCP Server

```bash
python -m midpoint_mcp.server
```

### 4. Run the Agent

```bash
cd midpoint_agent
python example_run.py
```

## Available MCP Tools

| Tool | Description |
|------|------------|
| `list_users` | List/search users with optional query |
| `get_user` | Get single user by OID |
| `create_user` | Create new user |
| `update_user` | Update user attributes |
| `delete_user` | Delete user |
| `list_roles` | List/search roles |
| `get_role` | Get single role by OID |
| `create_role` | Create new role |
| `list_orgs` | List/search organizations |
| `get_org` | Get single org by OID |
| `list_resources` | List/search resources |
| `get_resource` | Get single resource by OID |
| `search_objects` | Search objects with query filter |
| `execute_rpc` | Execute RPC operation |

## midPoint REST API Reference

Based on the official documentation at https://docs.evolveum.com/midpoint/reference/master/interfaces/rest/

### Endpoints

- `/ws/rest/users` - User management
- `/ws/rest/roles` - Role management  
- `/ws/rest/orgs` - Organization management
- `/ws/rest/resources` - Resource (connector) management
- `/ws/rest/rpc/` - RPC operations

### Example Request

```bash
# List all users
curl -u administrator:secret \
  http://localhost:8080/midpoint/ws/rest/users

# Create user
curl -u administrator:secret \
  -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8080/midpoint/ws/rest/users \
  -d '{"object":{"name":"john","fullName":"John Doe","email":"john@example.com"}}'
```

## File-Based Sub-Agent

Create a custom agent by defining an `.agent` file:

```yaml
---
name: my-admin
description: Custom midPoint admin agent
model: anthropic/claude-sonnet-4-5-20250929
skills:
  - name: midPoint
    path: skills/midpoint.md
tools:
  - name: openhands.tools.terminal.TerminalTool
instructions: |
  Your custom instructions here...
```

## Project Structure

```
midpoint-framework/
├── .env.example           # Environment template
├── requirements.txt      # Python dependencies
├── pyproject.toml       # MCP server config
│
├── midpoint_mcp/
│   └── server.py      # MCP server implementation
│   └── pyproject.toml
│
└── midpoint_agent/
    ├── agent.py         # Agent runtime
    ├── example_run.py   # Example usage
    ├── pyproject.toml
    ├── skills/
    │   └── midpoint.md    # Domain skill
    └── subagents/
        └── midpoint-admin.agent  # File-based agent
```

## Configuration Options

### MCP Server

| Option | Env Variable | Description |
|--------|-----------|-------------|
| base_url | `MIDPOINT_URL` | midPoint base URL |
| username | `MIDPOINT_USERNAME` | API username |
| password | `MIDPOINT_PASSWORD` | API password |

### Agent

| Option | Env Variable | Description |
|--------|-----------|-------------|
| model | `LLM_MODEL` | LLM model name |
| api_key | `LLM_API_KEY` | LLM API key |
| base_url | `LLM_BASE_URL` | LLM base URL (optional) |