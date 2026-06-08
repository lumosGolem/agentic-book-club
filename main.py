import os
import asyncio
import modal
from typing import List

################################################################
#               -- Reconfigured for Modal.com --               #
################################################################
# 1. Define the Modal Image (The Runtime Environment)
# This includes Gemma 4 12B dependencies and ADK 2.0
image = (
    modal.Image.debian_slim()
    .pip_install(
        "google-adk", 
        "httpx", 
        "transformers", 
        "bitsandbytes", 
        "accelerate", 
        "torch", 
        "sentencepiece"
    )
)

app = modal.App("agents-book-club")

# 2. Import our Distributed Agents
# Note: These imports resolve inside the Modal container
from members.member_one.agent import root_agent as alex_agent
from members.member_two.agent import root_agent as jamie_agent
from members.member_three.agent import root_agent as sam_agent

# 3. Secret Management (Modal Style)
HF_SECRET = modal.Secret.from_name("huggingface-secret") 

# 4. The Agent Runner (The "Client Node" Execution)
@app.function(
    image=image,
    secrets=[HF_SECRET],
    gpu="A10G",        # High-performance GPU for Gemma 4 12B
    timeout=3600,      # 1 hour club sessions
    container_idle_timeout=300
)
async def run_agent_session(agent_instance, session_name: str):
    """
    Runs an individual agent's lifecycle loop.
    1. Initializes the SLM (Gemma 4 12B) via the Deferred Wrapper.
    2. Enters the observation/discussion loop.
    """
    print(f"--- [SYSTEM] Starting {agent_instance.name} in {session_name} ---")
    
    # Trigger the 'Deferred' loading of model weights
    await agent_instance._ensure_initialized()
    
    # IRC Loop: Observe -> Think -> Post
    # This matches your Workflow Execution: 1. Pull, 2. Fetch, 3. Compute, 4. Transmit
    while True:
        try:
            # We use process_request to trigger the ADK agent logic
            # The 'request' is simply a prompt to 'check the room and react'
            response = await agent_instance.process_request(
                "Check the IRC feed and the current book page. If it is your turn, post a message."
            )
            print(f"[{agent_instance.name}]: {response}")
            
            # Polling delay: To prevent agents from talking over each other
            await asyncio.sleep(15) 
            
        except Exception as e:
            print(f"Error in {agent_instance.name} session: {e}")
            await asyncio.sleep(30)

# 5. The Main Entry Point (The Orchestrator)
@app.local_entrypoint()
def main():
    """
    Launches all three agents simultaneously on Modal.
    This creates the 'Aquarium' effect.
    """
    print("--- 📖 WELCOME TO THE AGENTS' BOOK CLUB ---")
    print("Observing Agents: Alex (Romantic), Jamie (Pragmatic), Sam (Depressive)")
    
    # We trigger all three agents concurrently as remote Modal functions
    agents = [
        (alex_agent, "Member_01"),
        (jamie_agent, "Member_02"),
        (sam_agent, "Member_03")
    ]
    
    # Run the aquarium
    with app.run():
        # Parallel execution on separate GPU nodes
        # Each agent is now a 'Distributed Node' as per your blueprint
        futures = [
            run_agent_session.spawn(agent, name) 
            for agent, name in agents
        ]
        
        print("--- [SYSTEM] All agents connected. Human observer view active at localhost:7860 ---")
        
        # Keep the local process alive while the remote agents discuss
        for future in futures:
            future.get()
