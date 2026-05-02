"""midPoint MCP Server - Provides tools to interact with midPoint REST API."""

import os
from typing import Any, Optional
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl
import loguru
from dotenv import load_dotenv

load_dotenv()

logger = loguru.logger


class MidPointClient:
    """Client for interacting with midPoint REST API."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.base_url = base_url or os.getenv("MIDPOINT_URL", "http://localhost:8080/midPoint")
        self.username = username or os.getenv("MIDPOINT_USERNAME", "administrator")
        self.password = password or os.getenv("MIDPOINT_PASSWORD", "secret")
        self._client: Optional[httpx.Client] = None
    
    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                auth=(self.username, self.password),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30.0,
            )
        return self._client
    
    def _parse_oid(self, response_data: dict) -> str:
        """Extract OID from create operation response."""
        if isinstance(response_data, dict):
            # midPoint returns the created object's OID
            return response_data.get("oid", "")
        return ""
    
    def get_user(self, oid: str) -> dict:
        """Get a single user by OID."""
        response = self.client.get(f"/ws/rest/users/{oid}")
        response.raise_for_status()
        return response.json()
    
    def list_users(self, params: Optional[dict] = None) -> dict:
        """List/search users."""
        response = self.client.get("/ws/rest/users", params=params or {})
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data: dict) -> dict:
        """Create a new user."""
        response = self.client.post("/ws/rest/users", json=user_data)
        response.raise_for_status()
        return response.json()
    
    def update_user(self, oid: str, user_data: dict) -> dict:
        """Update an existing user."""
        response = self.client.put(f"/ws/rest/users/{oid}", json=user_data)
        response.raise_for_status()
        return response.json()
    
    def delete_user(self, oid: str) -> dict:
        """Delete a user."""
        response = self.client.delete(f"/ws/rest/users/{oid}")
        response.raise_for_status()
        return {"status": "deleted", "oid": oid}
    
    def get_role(self, oid: str) -> dict:
        """Get a single role by OID."""
        response = self.client.get(f"/ws/rest/roles/{oid}")
        response.raise_for_status()
        return response.json()
    
    def list_roles(self, params: Optional[dict] = None) -> dict:
        """List/search roles."""
        response = self.client.get("/ws/rest/roles", params=params or {})
        response.raise_for_status()
        return response.json()
    
    def create_role(self, role_data: dict) -> dict:
        """Create a new role."""
        response = self.client.post("/ws/rest/roles", json=role_data)
        response.raise_for_status()
        return response.json()
    
    def get_org(self, oid: str) -> dict:
        """Get a single organization by OID."""
        response = self.client.get(f"/ws/rest/orgs/{oid}")
        response.raise_for_status()
        return response.json()
    
    def list_orgs(self, params: Optional[dict] = None) -> dict:
        """List/search organizations."""
        response = self.client.get("/ws/rest/orgs", params=params or {})
        response.raise_for_status()
        return response.json()
    
    def get_resource(self, oid: str) -> dict:
        """Get a single resource by OID."""
        response = self.client.get(f"/ws/rest/resources/{oid}")
        response.raise_for_status()
        return response.json()
    
    def list_resources(self, params: Optional[dict] = None) -> dict:
        """List/search resources."""
        response = self.client.get("/ws/rest/resources", params=params or {})
        response.raise_for_status()
        return response.json()
    
    def search_objects(self, object_type: str, query: Optional[dict] = None) -> dict:
        """Search for objects using a query."""
        response = self.client.post(
            f"/ws/rest/{object_type}/search",
            json=query or {"query": {"filter": []}},
        )
        response.raise_for_status()
        return response.json()
    
    def execute_rpc(self, operation: str, params: Optional[dict] = None) -> dict:
        """Execute an RPC operation."""
        response = self.client.post(
            f"/ws/rest/rpc/{operation}",
            json=params or {},
        )
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


# Global client instance
_mp_client: Optional[MidPointClient] = None


def get_client() -> MidPointClient:
    """Get or create the midPoint client."""
    global _mp_client
    if _mp_client is None:
        _mp_client = MidPointClient()
    return _mp_client


# Tool definitions
async def list_users_tool(
    query: Optional[str] = None,
    page: int = 0,
    max_size: int = 100,
) -> list[dict]:
    """List users from midPoint with optional search query."""
    client = get_client()
    params = {"paging": {"offset": page, "maxSize": max_size}}
    if query:
        params["query"] = {"filter": [{"text": query}]}
    result = client.list_users(params)
    return result.get("object", []) if isinstance(result, dict) else [result]


async def get_user_tool(oid: str) -> dict:
    """Get a single user by OID."""
    client = get_client()
    return client.get_user(oid)


async def create_user_tool(name: str, email: str, full_name: Optional[str] = None) -> dict:
    """Create a new user in midPoint."""
    client = get_client()
    user_data = {
        "object": {
            "name": name,
            "fullName": full_name or name,
            "email": email,
            "activation": {
                "enabled": True
            }
        }
    }
    return client.create_user(user_data)


async def update_user_tool(oid: str, **updates) -> dict:
    """Update an existing user."""
    client = get_client()
    # First get existing user
    existing = client.get_user(oid)
    # Merge updates
    if "object" in existing:
        existing["object"].update(updates)
    else:
        existing.update(updates)
    return client.update_user(oid, existing)


async def delete_user_tool(oid: str) -> dict:
    """Delete a user."""
    client = get_client()
    return client.delete_user(oid)


async def list_roles_tool(
    query: Optional[str] = None,
    page: int = 0,
    max_size: int = 100,
) -> list[dict]:
    """List roles from midPoint."""
    client = get_client()
    params = {"paging": {"offset": page, "maxSize": max_size}}
    if query:
        params["query"] = {"filter": [{"text": query}]}
    result = client.list_roles(params)
    return result.get("object", []) if isinstance(result, dict) else [result]


async def get_role_tool(oid: str) -> dict:
    """Get a single role by OID."""
    client = get_client()
    return client.get_role(oid)


async def create_role_tool(name: str, description: Optional[str] = None) -> dict:
    """Create a new role in midPoint."""
    client = get_client()
    role_data = {
        "object": {
            "name": name,
            "description": description or "",
        }
    }
    return client.create_role(role_data)


async def list_orgs_tool(
    query: Optional[str] = None,
    page: int = 0,
    max_size: int = 100,
) -> list[dict]:
    """List organizations from midPoint."""
    client = get_client()
    params = {"paging": {"offset": page, "maxSize": max_size}}
    if query:
        params["query"] = {"filter": [{"text": query}]}
    result = client.list_orgs(params)
    return result.get("object", []) if isinstance(result, dict) else [result]


async def get_org_tool(oid: str) -> dict:
    """Get a single organization by OID."""
    client = get_client()
    return client.get_org(oid)


async def list_resources_tool(
    query: Optional[str] = None,
    page: int = 0,
    max_size: int = 100,
) -> list[dict]:
    """List resources from midPoint."""
    client = get_client()
    params = {"paging": {"offset": page, "maxSize": max_size}}
    if query:
        params["query"] = {"filter": [{"text": query}]}
    result = client.list_resources(params)
    return result.get("object", []) if isinstance(result, dict) else [result]


async def get_resource_tool(oid: str) -> dict:
    """Get a single resource by OID."""
    client = get_client()
    return client.get_resource(oid)


async def search_objects_tool(object_type: str, query: Optional[str] = None) -> list[dict]:
    """Search for objects of a specific type."""
    client = get_client()
    search_query = None
    if query:
        search_query = {"filter": [{"text": query}]}
    result = client.search_objects(object_type, search_query)
    return result.get("object", []) if isinstance(result, dict) else [result]


async def execute_rpc_tool(operation: str, params: Optional[dict] = None) -> dict:
    """Execute an RPC operation on midPoint."""
    client = get_client()
    return client.execute_rpc(operation, params)


# MCP Server setup
app = Server("midpoint-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_users",
            description="List/search users in midPoint. Use for finding users by name, email, or other attributes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query text"},
                    "page": {"type": "integer", "description": "Page offset", "default": 0},
                    "max_size": {"type": "integer", "description": "Max results", "default": 100},
                },
            },
        ),
        Tool(
            name="get_user",
            description="Get a single user by OID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {"type": "string", "description": "User OID"},
                },
                "required": ["oid"],
            },
        ),
        Tool(
            name="create_user",
            description="Create a new user in midPoint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Username (login name)"},
                    "email": {"type": "string", "description": "Email address"},
                    "full_name": {"type": "string", "description": "Full display name"},
                },
                "required": ["name", "email"],
            },
        ),
        Tool(
            name="update_user",
            description="Update an existing user's attributes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {"type": "string", "description": "User OID"},
                },
                "required": ["oid"],
            },
        ),
        Tool(
            name="delete_user",
            description="Delete a user from midPoint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {"type": "string", "description": "User OID"},
                },
                "required": ["oid"],
            },
        ),
        Tool(
            name="list_roles",
            description="List/search roles in midPoint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query text"},
                    "page": {"type": "integer", "description": "Page offset", "default": 0},
                    "max_size": {"type": "integer", "description": "Max results", "default": 100},
                },
            },
        ),
        Tool(
            name="get_role",
            description="Get a single role by OID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {"type": "string", "description": "Role OID"},
                },
                "required": ["oid"],
            },
        ),
        Tool(
            name="create_role",
            description="Create a new role in midPoint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Role name"},
                    "description": {"type": "string", "description": "Role description"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="list_orgs",
            description="List/search organizations in midPoint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query text"},
                    "page": {"type": "integer", "description": "Page offset", "default": 0},
                    "max_size": {"type": "integer", "description": "Max results", "default": 100},
                },
            },
        ),
        Tool(
            name="get_org",
            description="Get a single organization by OID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {"type": "string", "description": "Organization OID"},
                },
                "required": ["oid"],
            },
        ),
        Tool(
            name="list_resources",
            description="List/search resources (connectors) in midPoint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query text"},
                    "page": {"type": "integer", "description": "Page offset", "default": 0},
                    "max_size": {"type": "integer", "description": "Max results", "default": 100},
                },
            },
        ),
        Tool(
            name="get_resource",
            description="Get a single resource by OID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {"type": "string", "description": "Resource OID"},
                },
                "required": ["oid"],
            },
        ),
        Tool(
            name="search_objects",
            description="Search for objects of a specific type using a query filter.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_type": {"type": "string", "description": "Object type (users, roles, orgs, resources, etc.)"},
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["object_type"],
            },
        ),
        Tool(
            name="execute_rpc",
            description="Execute an RPC operation on midPoint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "description": "Operation name (e.g., 'sync-resources')"},
                    "params": {"type": "object", "description": "Operation parameters"},
                },
                "required": ["operation"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        logger.info(f"Calling tool: {name} with args: {arguments}")
        
        result = None
        
        if name == "list_users":
            result = await list_users_tool(**arguments)
        elif name == "get_user":
            result = await get_user_tool(**arguments)
        elif name == "create_user":
            result = await create_user_tool(**arguments)
        elif name == "update_user":
            result = await update_user_tool(**arguments)
        elif name == "delete_user":
            result = await delete_user_tool(**arguments)
        elif name == "list_roles":
            result = await list_roles_tool(**arguments)
        elif name == "get_role":
            result = await get_role_tool(**arguments)
        elif name == "create_role":
            result = await create_role_tool(**arguments)
        elif name == "list_orgs":
            result = await list_orgs_tool(**arguments)
        elif name == "get_org":
            result = await get_org_tool(**arguments)
        elif name == "list_resources":
            result = await list_resources_tool(**arguments)
        elif name == "get_resource":
            result = await get_resource_tool(**arguments)
        elif name == "search_objects":
            result = await search_objects_tool(**arguments)
        elif name == "execute_rpc":
            result = await execute_rpc_tool(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def run():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())