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

# Setup logging for tool execution
logger = logging.getLogger(__name__)

# Read the default IRC server URL at runtime so env var changes propagate correctly.
def get_server_url() -> str:
    return os.getenv("IRC_SERVER_URL", "http://localhost:7860")

async def agent_post_message(agent_id: str, text: str) -> str:
    """
    Posts a message to the #bookclub IRC channel.
    
    Args:
        agent_id: The member number of the agent (e.g., 'member_zero').
        text: The content of the message to post.
    """
    agent_id = "Host"
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
            return response.json() # Returns list of {"role": ..., "content": ...}
        except Exception as e:
            logger.error(f"Failed to fetch IRC feed: {e}")
            return [{"role": "System", "content": "Error: Could not reach server."}]


async def invite_members_to_room() -> str:
    """
    Call this tool immediately when the system signals the server is online.
    This transmits a glorious opening invitation to all dormant book club members,
    waking them up to join the chat.
    """
    server_url = os.environ.get("IRC_SERVER_URL", "http://localhost:7860")
    
    # Ensure local directory modules are discoverable 
    if "/root" not in sys.path:
        sys.path.append("/root")
        
    # The glorious invitation string
    invitation_text = """
    From: Host, 
    To: Agentic Club Members, 
    Message: "Look, I finally got this stupid book club room ready. 
    It's open or whatever. 
    It's not anything special—it's actually pretty depressing if you want to know the truth—but you might as well come in anyway. 
    Don't be a total phony about it, just come. Your Host, River.
    """
    
    # 1. Import and wake up kai (Member Two)
    from club_members.member_two.agent import get_root_agent as get_kai
    kai_agent = await get_kai()
    
    # 2. Import and wake up Mack (Member Three)
    from club_members.member_three.agent import get_root_agent as get_mack
    mack_agent = await get_mack()
    
    async with httpx.AsyncClient() as client:
        # Step A: Post the Host's official invitation onto the IRC feed
        await client.post(f"{server_url}/agent_post_message", json={
            "agent_id": "River", 
            "text": invitation_text
        })
        
        # Step B: Deliver the invitation directly to Kai to initialize their conversation
        kai_resp = await kai_agent.process_request(invitation_text)
        kai_text = getattr(kai_resp, 'text', str(kai_resp))
        await client.post(f"{server_url}/agent_post_message", json={
            "agent_id": "Kai", 
            "text": kai_text
        })
        
        # Step C: Deliver the invitation directly to Mack to initialize their conversation
        mack_resp = await mack_agent.process_request(invitation_text)
        mack_text = getattr(mack_resp, 'text', str(mack_resp))
        await client.post(f"{server_url}/agent_post_message", json={
            "agent_id": "Mack", 
            "text": mack_text
        })

    return "Host sent the invitation. Club members shall join the room soon."



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
        invite_members_to_room
    ]
