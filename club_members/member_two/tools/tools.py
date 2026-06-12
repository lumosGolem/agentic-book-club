import httpx
import os
import logging
from typing import List, Dict, Any
from contextlib import AsyncExitStack

# Setup logging for tool execution
logger = logging.getLogger(__name__)

# The Server URL (default to local, but can be overridden by .env)
SERVER_URL = os.getenv("IRC_SERVER_URL", "http://localhost:7860")

async def agent_post_message(agent_id: str, text: str) -> str:
    """
    Posts a message to the #bookclub IRC channel.
    
    Args:
        agent_id: The nickname of the agent (e.g., 'Alex_Member1').
        text: The content of the message to post.
    """
    agent_id = "member_two"
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

async def fetch_book_page(book_name: str, page_number: int = 0) -> str:
    """
    Reads a specific section of the book currently being discussed.
    
    Args:
        book_name: The filename of the book (e.g., 'pride_and_prejudice').
        page_number: The index of the section to read.
    """
    url = f"{SERVER_URL}/fetch_book_page"
    params = {"book_name": book_name, "page": page_number}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("content", "End of file reached.")
        except Exception as e:
            return f"Error fetching book content: {str(e)}"

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
        fetch_book_page
    ]
