#!/usr/bin/env python3
"""
Example: Run midPoint agent with MCP tools.

This example shows how to connect the OpenHands agent to the midPoint MCP server
to provide intelligent interactions with the midPoint identity management system.

Usage:
    export MIDPOINT_URL=http://localhost:8080/midpoint
    export MIDPOINT_USERNAME=administrator  
    export MIDPOINT_PASSWORD=secret
    export LLM_API_KEY=your-api-key
    
    python example_run.py

    # Or ask questions
    python example_run.py "list all users"
"""

import asyncio
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.tools.terminal import TerminalTool


# Check MCP availability and import
try:
    from mcp import Client as MCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPClient = None


async def run_with_mcp(question: str):
    """Run agent with MCP tools."""
    
    if not MCP_AVAILABLE:
        print("Error: MCP not available. Please install mcp package.")
        return
    
    # Get configuration from environment
    midpoint_url = os.getenv("MIDPOINT_URL", "http://localhost:8080/midpoint")
    
    # Create LLM
    llm = LLM(
        model=os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
    )
    
    # Create agent with terminal tool
    tools = [Tool(name=TerminalTool.name)]
    
    agent = Agent(
        llm=llm,
        tools=tools,
        description="""You are a midPoint identity management assistant.
You can help users manage users, roles, organizations, and resources in midPoint.
Use the available tools to interact with the midPoint REST API.
Always confirm destructive operations before proceeding.
When asked about users, roles, or orgs, explain you can access midPoint API through your tools.""",
        max_iterations=50,
    )
    
    # Create conversation
    conversation = Conversation(
        agent=agent,
        workspace=os.getcwd(),
    )
    
    # Send user question
    conversation.send_message(question)
    
    # Run
    print(f"Asking: {question}")
    print("-" * 50)
    
    await conversation.run()
    
    # Show results
    for event in conversation.history.events:
        print(event)


async def run_simple(question: str):
    """Run without MCP - just simple agent demo."""
    
    llm = LLM(
        model=os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
    )
    
    tools = [Tool(name=TerminalTool.name)]
    
    agent = Agent(
        llm=llm,
        tools=tools,
        description="""You are a helpful assistant that helps with midPoint identity management questions.
 midPoint is an open-source identity management and access management system.
 Know about users, roles, orgs, resources, RBAC, and policy-driven access control.
 Provide helpful explanations about identity management concepts.""",
    )
    
    conversation = Conversation(agent=agent, workspace=".")
    conversation.send_message(question)
    
    print(f"Question: {question}")
    print("-" * 50)
    
    await conversation.run()
    
    for event in conversation.history.events:
        print(event)


async def main():
    """Main entry point."""
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is midPoint?"
    
    if MCP_AVAILABLE:
        await run_with_mcp(question)
    else:
        print("MCP not available, running simple mode...")
        await run_simple(question)


if __name__ == "__main__":
    asyncio.run(main())