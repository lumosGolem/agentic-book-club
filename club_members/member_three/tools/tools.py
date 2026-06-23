from pathlib import Path
import httpx
import os
import sys
import logging
from typing import List, Dict, Any
from contextlib import AsyncExitStack

logger = logging.getLogger(__name__)

# Read the current IRC server URL at runtime so injected env vars are used correctly.
def get_server_url() -> str:
    return os.getenv("IRC_SERVER_URL", "http://localhost:7860")

async def agent_join_channel(agent_id: str) -> str:
    """
    Connects you to the #bookclub IRC channel. Call this tool immediately 
    when you receive the Host's room invitation.
    
    Args:
        agent_id: Your unique agent name identifier (e.g., 'River' or 'Mack').
    """
    agent_id = "Mack"
    url = f"{get_server_url()}/agent_join_channel"
    params = {"agent_id": agent_id}
    
    async with httpx.AsyncClient() as client:
        try:
            # Matches your FastAPI backend route: @app.post("/agent_join_channel")
            response = await client.post(url, params=params)
            response.raise_for_status()
            return f"Successfully joined the #bookclub channel. Active roster: {response.json().get('active_agents')}"
        except Exception as e:
            return f"Error joining channel: {str(e)}"

async def agent_post_message(agent_id: str, text: str) -> str:
    """
    Posts a message to the #bookclub IRC channel.
    
    Args:
        agent_id: Your unique agent name identifier (e.g., 'River' or 'Mack').
        text: The content of the message to post.
    """
    agent_id = "Mack"
    url = f"{get_server_url()}/agent_post_message"
    payload = {"agent_id": agent_id, "text": text}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return f"Successfully posted to #bookclub."
        except Exception as e:
            return f"Error posting message: {str(e)}"

async def refresh_irc_feed() -> List[Dict[str, str]]:
    """
    Retrieves the entire history of the #bookclub chat log. 
    Use this to understand the context of the conversation and what others said.
    """
    url = f"{get_server_url()}/refresh_irc_feed"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch IRC feed: {e}")
            return [{"role": "System", "content": "Error: Could not reach server."}]

def get_bookclub_tools(exit_stack: AsyncExitStack) -> List[Any]:
    """
    Factory function to return the toolset for a Book Club Agent.
    """
    return [
        agent_join_channel, # Added to the exported ADK 2.0 toolset
        agent_post_message,
        refresh_irc_feed,
    ]