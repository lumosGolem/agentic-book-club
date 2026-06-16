from pathlib import Path
import httpx
import os
import sys
import logging
from typing import List, Dict, Any
from contextlib import AsyncExitStack
# Cross-directory absolute import pulling straight from root module pathing

### Carry over book-store function
PROJECT_ROOT = Path(__file__).resolve().parents[3] 
sys.path.insert(0, str(PROJECT_ROOT))

from book_store.tools.tools import search_shared_bookstore

# Setup logging for tool execution
logger = logging.getLogger(__name__)

# The Server URL (default to local, but can be overridden by .env)
SERVER_URL = os.getenv("IRC_SERVER_URL", "")

async def agent_post_message(agent_id: str, text: str) -> str:
    """
    Posts a message to the #bookclub IRC channel.
    
    Args:
        agent_id: The member number of the agent (e.g., 'member_zero').
        text: The content of the message to post.
    """
    agent_id = "member_one"
    url = f"{SERVER_URL}/agent_post_message"
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
    url = f"{SERVER_URL}/refresh_irc_feed"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json() # Returns list of {"role": ..., "content": ...}
        except Exception as e:
            logger.error(f"Failed to fetch IRC feed: {e}")
            return [{"role": "System", "content": "Error: Could not reach server."}]

def get_bookclub_tools(exit_stack: AsyncExitStack) -> List[Any]:
    """
    Factory function to return the toolset for a Book Club Agent.
    In ADK 2.0, we simply return the list of async functions.
    """
    # The exit_stack can be used here if we wanted to maintain a 
    # persistent httpx.AsyncClient throughout the agent's lifecycle.
    # For now, we use a functional approach.
    
    return [
        agent_post_message,
        refresh_irc_feed,
        search_shared_bookstore
    ]
