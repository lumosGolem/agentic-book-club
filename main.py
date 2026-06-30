import os
import sys
import modal

# Define the container image with its system dependencies and local workspace files
image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install(
        "google-adk>=2.2.0",
        "httpx>=0.27.0",
        "gradio",
        "fastapi",
        "uvicorn",
        "pydantic>=2.0.0",
        "python-dotenv",
        "gradio-client",
    )
    # Modern Modal 1.0 way to mount your code instead of using modal.Mount.
    # The 'ignore' list prevents uploading junk files and local virtualenvs.
    .add_local_dir(
        ".", 
        "/root", 
        ignore=[".venv", "__pycache__", ".git", "*.pyc", "*.gitattributes"]
    )
)

app = modal.App("agentic-book-club")

# Import the FastAPI/Gradio app defined in your app.py
try:
    from app import app as fastapi_app
except ImportError:
    # Fallback to prevent deploy failures if file paths are organized differently
    fastapi_app = None

HF_TOKEN = modal.Secret.from_name("huggingface-secret") 
IRC_SERVER_URL = modal.Secret.from_name("IRC_SERVER_URL")
GEMINI_API_KEY = modal.Secret.from_name("GEMINI_API_KEY")

@app.asgi_app(
    image=image, 
    secrets=[HF_TOKEN, IRC_SERVER_URL, GEMINI_API_KEY]
)
def serve():
    if fastapi_app is None:
        raise ImportError(
            "Could not import 'app' from app.py. Please verify your local folder layout."
        )
    return fastapi_app

@app.function(
    image=image,
    secrets=[HF_TOKEN, IRC_SERVER_URL, GEMINI_API_KEY],
    gpu="A10G",               
    timeout=3600,
    scaledown_window=300
)
async def trigger_host_node(irc_url: str):
    """
    Wakes up the Host agent inside the single container. 
    The Host then executes its tool to invite and initialize the other members.
    """
    os.environ["IRC_SERVER_URL"] = irc_url
    
    # Ensure Python can resolve modules in the root directory
    if "/root" not in sys.path:
        sys.path.append("/root")
    
    # Import the Host Agent lazily inside the container context
    from club_members.member_two.agent import get_root_agent
    host_agent = await get_root_agent()
    
    # Holden Caulfield style directive to push the Host to open the room
    system_trigger_prompt = (
        "The server is online. Go open up that stupid book club room "
        "and tell the guys to get in here."
    )
    
    print(f"--- [PROJECT CONTAINER] Injecting trigger: {system_trigger_prompt} ---")
    
    # This call fires the host agent, which triggers its internal invitation tool
    response = await host_agent.process_request(system_trigger_prompt)
    output_text = getattr(response, 'text', str(response))
    
    print(f"--- [PROJECT CONTAINER] Host Execution Complete: {output_text} ---")
    return output_text
