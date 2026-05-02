# midPoint Agent Skill

## Overview

This skill provides the agent with knowledge about the midPoint Identity and Access Management system and its REST API. The agent can interact with midPoint through MCP tools to manage users, roles, organizations, and resources.

## midPoint REST API Basics

midPoint exposes a RESTful API at `/ws/rest/` endpoint. Common operations:

- **Users**: `/ws/rest/users` - Manage user accounts
- **Roles**: `/ws/rest/roles` - Manage roles (RBAC)
- **Orgs**: `/ws/rest/orgs` - Manage organizations
- **Resources**: `/ws/rest/resources` - Manage connected resources (connectors)
- **RPC**: `/ws/rest/rpc/` - Execute operations like sync, recompute

## Object Structure

midPoint objects follow this structure:

```
object:
  oid: <unique-id>
  name: <identifier>
  displayName: <display-name>
  activation:
    enabled: true|false
    validFrom: <timestamp>
    validTo: <timestamp>
  credentials:
    password: <password-value>
  assignment:
    - targetRef:
        oid: <role-or-org-oid>
        type: <RoleType|OrgType>
```

## Common Operations

### User Management
- List users: `GET /ws/rest/users`
- Get user: `GET /ws/rest/users/{oid}`
- Create user: `POST /ws/rest/users`
- Update user: `PUT /ws/rest/users/{oid}`
- Delete user: `DELETE /ws/rest/users/{oid}`

### Role Management
- List roles: `GET /ws/rest/roles`
- Get role: `GET /ws/rest/roles/{oid}`
- Create role: `POST /ws/rest/roles`
- Assign role to user: Add `assignment` with `targetRef` to user object

### Search
- Use `POST /ws/rest/{type}/search` with query filter
- Filter types: `equal`, `like`, `and`, `or`, `not`

## Configuration

The agent connects to midPoint using these environment variables:
- `MIDPOINT_URL` - Base URL (default: http://localhost:8080/midPoint)
- `MIDPOINT_USERNAME` - Username (default: administrator)
- `MIDPOINT_PASSWORD` - Password (default: secret)

## Usage Guidelines

1. **Always confirm destructive operations** (delete) with the user
2. **Use search first** to find existing objects before creating
3. **Include all required fields** when creating objects
4. **Check activation status** when troubleshooting user access issues
5. **Use RPC operations** for bulk operations like sync/recompute

## Available Tools (MCP)

When MCP server is connected, use these tools:
- `list_users`, `get_user`, `create_user`, `update_user`, `delete_user`
- `list_roles`, `get_role`, `create_role`
- `list_orgs`, `get_org`
- `list_resources`, `get_resource`
- `search_objects`, `execute_rpc`

## Example Tasks

- "Find all enabled users with email containing @company.com"
- "Create a new user john.doe with email john@company.com"
- "Assign the HR Manager role to user jane.smith"
- "List all resources and their status"
- "Sync the LDAP directory resource"