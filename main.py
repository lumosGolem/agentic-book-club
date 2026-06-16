import os
import asyncio
import modal

image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install(
        "google-adk>=2.2.0", 
        "httpx", 
        "gradio-client",
    )
)

app = modal.App("agentic-book-club")

HF_TOKEN = modal.Secret.from_name("huggingface-secret") 
IRC_SERVER_URL = modal.Secret.from_name("IRC_SERVER_URL")
GEMINI_API_KEY = modal.Secret.from_name("GEMINI_API_TOKEN")

local_code_mount = modal.Mount.from_local_dir(".", remote_path="/root")

@app.function(
    image=image,
    secrets=[HF_TOKEN, IRC_SERVER_URL, GEMINI_API_KEY],
    gpu="A10G",               
    timeout=3600,             
    container_idle_timeout=300,
    mounts=[local_code_mount]
)
async def run_agent_session(member_id: str, session_name: str, irc_url: str):
    print(f"--- [SYSTEM] Remote Node Initialized. Booting {member_id} ({session_name}) ---")
    
    os.environ["IRC_SERVER_URL"] = irc_url
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    
    # Fix: Ensure python looks in /root for your club_members module
    import sys
    if "/root" not in sys.path:
        sys.path.append("/root")
    
    if member_id == "member_one":
        from club_members.member_one.agent import root_agent as agent_instance
    elif member_id == "member_two":
        from club_members.member_two.agent import root_agent as agent_instance
    elif member_id == "member_three":
        from club_members.member_three.agent import root_agent as agent_instance
    else:
        raise ValueError(f"Unknown agent member identifier: {member_id}")

    await agent_instance._ensure_initialized()
    
    print(f"--- [SYSTEM] {agent_instance.name} Model Loaded. Entering IRC Loop ---")
    
    while True:
        try:
            response = await agent_instance.process_request(
                "Read the latest book club channel messages. If a book club discussion is active, share your unique perspective."
            )
            # Extracted attribute depending on exact ADK schema output
            output_text = getattr(response, 'text', str(response))
            print(f"[{agent_instance.name} Response Generated]: {output_text}")
            
            await asyncio.sleep(20) 
            
        except Exception as e:
            print(f"Error in {agent_instance.name} remote execution loop: {e}")
            await asyncio.sleep(30)

# The Main Orchestrator
@app.local_entrypoint()
def main():
    # Fix: Fetch environment token safely
    irc_server_url = os.environ.get("IRC_SERVER_URL", "https://lumosgolem-agents-book-club.hf.space")
    
    print("--- 📖 WELCOME TO THE DISTRIBUTED AGENTS' BOOK CLUB ---")
    print(f"Connecting observer nodes to IRC Hub: {irc_server_url}")
    
    agent_mappings = [
        ("member_one", "Kai"),
        ("member_two", "River"),
        ("member_three", "Mack"),
    ]
    
    futures = []
    # Fix: Removed 'with app.run():' context block because it is handled by the local entrypoint
    for member_id, description in agent_mappings:
        print(f"Deploying {description} to active GPU instance...")
        fut = run_agent_session.spawn(member_id, description, irc_server_url)
        futures.append(fut)
        
    print("--- [SYSTEM] All distributed agents launched. Observing feed live ---")
    
    for future in futures:
        future.get()