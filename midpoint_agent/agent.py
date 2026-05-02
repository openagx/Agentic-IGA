"""
midPoint Agent - AI-powered agent to interact with midPoint via MCP.

This agent uses the OpenHands SDK with LangGraph and MCP integration to provide
intelligent question-answering and operations against the midPoint identity management system.
"""

import os
import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional

from openhands.sdk import LLM, Agent, Conversation, Tool


# Terminal tool from openhands-tools
try:
    from openhands.tools.terminal import TerminalTool
except ImportError:
    TerminalTool = None


# Configuration
@dataclass
class MidPointAgentConfig:
    """Configuration for the midPoint agent."""
    
    # LLM settings
    model: str = os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929")
    api_key: Optional[str] = os.getenv("LLM_API_KEY")
    base_url: Optional[str] = os.getenv("LLM_BASE_URL")
    
    # midPoint connection
    midpoint_url: str = os.getenv("MIDPOINT_URL", "http://localhost:8080/midpoint")
    midpoint_username: str = os.getenv("MIDPOINT_USERNAME", "administrator")
    midpoint_password: str = os.getenv("MIDPOINT_PASSWORD", "secret")
    
    # Agent settings
    max_iterations: int = 100
    confirmation_mode: bool = False


class MidPointAgentRuntime:
    """Runtime for the midPoint agent with MCP integration."""
    
    def __init__(self, config: Optional[MidPointAgentConfig] = None):
        self.config = config or MidPointAgentConfig()
        self._llm: Optional[LLM] = None
        self._agent: Optional[Agent] = None
    
    @property
    def llm(self) -> LLM:
        if self._llm is None:
            self._llm = LLM(
                model=self.config.model,
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
        return self._llm
    
    @property
    def agent(self) -> Agent:
        if self._agent is None:
            tools = []
            
            # Add terminal tool if available
            if TerminalTool:
                tools.append(Tool(name=TerminalTool.name))
            
            self._agent = Agent(
                llm=self.llm,
                tools=tools,
                description="""You are a midPoint identity management assistant. 
You can help users manage users, roles, organizations, and resources in midPoint.
Use MCP tools to interact with the midPoint REST API when available.
Always confirm destructive operations before proceeding.""",
                max_iterations=self.config.max_iterations,
            )
        return self._agent
    
    async def chat(self, message: str, workspace: str = ".") -> str:
        """Send a message to the agent and get response."""
        conversation = Conversation(
            agent=self.agent,
            workspace=workspace,
        )
        
        conversation.send_message(message)
        await conversation.run()
        
        # Return the last message from agent
        events = conversation.history.events
        if events:
            return str(events[-1])
        return "No response"


async def create_agent(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    midpoint_url: Optional[str] = None,
) -> MidPointAgentRuntime:
    """Create a configured midPoint agent."""
    config = MidPointAgentConfig(
        model=model or os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929"),
        api_key=api_key or os.getenv("LLM_API_KEY"),
        midpoint_url=midpoint_url or os.getenv("MIDPOINT_URL", "http://localhost:8080/midpoint"),
    )
    return MidPointAgentRuntime(config)