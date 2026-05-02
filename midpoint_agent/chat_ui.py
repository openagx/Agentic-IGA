"""
Simple chat UI for midPoint agent using FastAPI.
"""

import os
import asyncio
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.tools.terminal import TerminalTool

app = FastAPI(title="midPoint Agent Chat UI")


class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None


# Agent configuration
def get_llm():
    return LLM(
        model=os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
    )


def get_agent():
    llm = get_llm()
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name)],
        description="""You are a helpful assistant for midPoint identity management.
You help users manage users, roles, organizations, and resources in midPoint.
Provide clear, helpful responses.""",
        max_iterations=50,
    )


@app.get("/", response_class=HTMLResponse)
async def chat_ui():
    return """<!DOCTYPE html>
<html>
<head>
    <title>midPoint Agent Chat</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px; margin: 0 auto; padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        #chat-container {
            background: white; border-radius: 8px; padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 60vh; overflow-y: auto;
        }
        .message { margin: 10px 0; padding: 12px 16px; border-radius: 8px; }
        .user { background: #007acc; color: white; margin-left: 20%; }
        .assistant { background: #e9e9e9; color: #333; margin-right: 20%; }
        .system { background: #fff3cd; color: #856404; font-style: italic; }
        #input-container {
            display: flex; gap: 10px; margin-top: 20px;
        }
        input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        button {
            padding: 12px 24px; background: #007acc; color: white; border: none;
            border-radius: 4px; cursor: pointer; font-size: 16px;
        }
        button:hover { background: #005a99; }
        button:disabled { background: #ccc; }
        .loading { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>🤖 midPoint Agent Chat</h1>
    <div id="chat-container"></div>
    <div id="input-container">
        <input type="text" id="message" placeholder="Ask about users, roles, orgs in midPoint..." autofocus>
        <button id="send">Send</button>
    </div>
    <script>
        const container = document.getElementById('chat-container');
        const input = document.getElementById('message');
        const sendBtn = document.getElementById('send');
        
        function addMessage(text, role) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.textContent = text;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
        
        async function sendMessage() {
            const message = input.value.trim();
            if (!message) return;
            
            input.value = '';
            addMessage(message, 'user');
            
            sendBtn.disabled = true;
            addMessage('Thinking...', 'system');
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message})
                });
                const data = await response.json();
                
                // Remove loading message
                container.removeChild(container.lastChild);
                addMessage(data.response, 'assistant');
            } catch (e) {
                container.removeChild(container.lastChild);
                addMessage('Error: ' + e.message, 'system');
            }
            
            sendBtn.disabled = false;
            input.focus();
        }
        
        sendBtn.onclick = sendMessage;
        input.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
    </script>
</body>
</html>"""


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent and get response."""
    try:
        agent = get_agent()
        conversation = Conversation(agent=agent, workspace=".")
        
        conversation.send_message(request.message)
        await conversation.run()
        
        # Get last response
        response_text = ""
        for event in conversation.history.events:
            response_text = str(event)
        
        return ChatResponse(response=response_text or "No response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)