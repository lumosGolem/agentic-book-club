import os
import sys
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

async def trigger_host_node(irc_url: str):
    """
    Wakes up the Host agent inside the single container. 
    The Host then executes its tool to invite and initialize the other members.
    """
    os.environ["IRC_SERVER_URL"] = irc_url
    
    # Ensure Python can resolve modules in the mounted root directory
    if "/root" not in sys.path:
        sys.path.append("/root")
    
    # Import the Host Agent (assumed to be member_one here; adjust path if needed)
    from club_members.member_one.agent import get_root_agent
    host_agent = await get_root_agent()
    
    # Holden Caulfield style directive to push the Host to open the room
    system_trigger_prompt = (
        "The server is online. Go open up that stupid book club room "
        "and tell the guys to get in here."
    )
    
    print(f"--- [AQUARIUM CONTAINER] Injecting trigger: {system_trigger_prompt} ---")
    
    # This call fires the host agent, which triggers its internal invitation tool
    response = await host_agent.process_request(system_trigger_prompt)
    output_text = getattr(response, 'text', str(response))
    
    print(f"--- [AQUARIUM CONTAINER] Host Execution Complete: {output_text} ---")
    return output_text