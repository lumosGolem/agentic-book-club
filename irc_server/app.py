import os
import glob
import subprocess
import datetime
import gradio as gr
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# --- GLOBAL STATE CHANNEL BUS ---
# Store messages with timestamps and role identifiers
GLOBAL_CHANNEL_LOG = [
    {
        "role": "assistant", 
        "content": "⚡ [SYSTEM] IRC Server Online. Port 7860 active. Waiting for orchestrator..."
    }
]

# Track currently connected automated agent nodes
ACTIVE_AGENTS = set()

# --- DATA MODELS ---
class Message(BaseModel):
    agent_id: str
    text: str

# --- API SOCKET ENDPOINTS ---

@app.post("/agent_join_channel")
async def join(agent_id: str):
    """Called by Modal agents when initializing their cloud session."""
    ACTIVE_AGENTS.add(agent_id)
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    msg = {
        "role": "assistant", 
        "content": f"📡 [{timestamp}] *** JOIN: Agent '{agent_id}' has established connection to #bookclub"
    }
    GLOBAL_CHANNEL_LOG.append(msg)
    return {"status": "connected", "active_agents": list(ACTIVE_AGENTS)}

@app.get("/refresh_irc_feed")
async def refresh():
    """Allows active agent brains to scrape historical logs of the chat."""
    return GLOBAL_CHANNEL_LOG

@app.post("/agent_post_message")
async def post(msg: Message):
    """Receives reasoning/replies sent from the Modal GPU containers."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = {
        "role": msg.agent_id, 
        "content": f"[{timestamp}] <{msg.agent_id}> {msg.text}"
    }
    GLOBAL_CHANNEL_LOG.append(entry)
    # Ensure they are registered in the active roster
    ACTIVE_AGENTS.add(msg.agent_id)
    return {"status": "posted"}

@app.get("/fetch_book_page")
async def fetch_book(book_name: str, page: int = 0):
    """
    Simulated File System API. 
    Agents read 2000-character slices of documents from HF storage.
    """
    search_pattern = f"../book-store/**/{book_name}.md"
    matches = glob.glob(search_pattern, recursive=True)
    
    if not matches:
        # Fallback search matching localized directory structures
        search_pattern_local = f"book-store/**/{book_name}.md"
        matches = glob.glob(search_pattern_local, recursive=True)

    if not matches:
        raise HTTPException(status_code=404, detail=f"Book '{book_name}' not found.")
    
    try:
        path = matches[0]
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            start = page * 2000
            end = start + 2000
            return {
                "book": book_name, 
                "content": content[start:end],
                "has_more": len(content) > end
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_modal_orchestrator():
    """Triggers main.py in the background to spin up Modal's cluster."""
    # Pre-flight check to verify entrypoint scripts
    if not os.path.exists("main.py"):
        return "❌ Error: Could not find 'main.py' in workspace. Ensure repository files are aligned."
        
    try:
        # Start main.py as an isolated background task
        subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return "🚀 Modal orchestrator started in background! GPU nodes spinning up (takes ~1-2 min)."
    except Exception as e:
        return f"❌ Failed to run main.py: {str(e)}"

terminal_css = """
/* Theme foundation */
body, .gradio-container {
    background-color: #060913 !important;
    font-family: 'Courier New', Courier, monospace !important;
}

/* Header style styling */
#terminal-header {
    background: linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%);
    border: 1px solid #312e81;
    border-bottom: 3px solid #6366f1;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    font-weight: bold;
    font-size: 1.35rem;
    color: #818cf8;
    text-shadow: 0 0 10px rgba(99, 102, 241, 0.4);
    margin-bottom: 20px;
    letter-spacing: 2px;
}

/* Chat container styling */
#irc-log {
    background-color: #02040a !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    padding: 12px !important;
    height: 520px !important;
    box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.8) !important;
}

/* Message Bubble customization */
#irc-log .message-wrap {
    background: transparent !important;
}

#irc-log .message {
    background-color: #0f172a !important;
    border-left: 3px solid #818cf8 !important;
    color: #e2e8f0 !important;
    border-radius: 4px !important;
    margin: 4px 0 !important;
    padding: 8px 12px !important;
    font-size: 0.92rem !important;
    line-height: 1.4 !important;
}

/* Custom colors depending on role names */
#irc-log .message[data-role="assistant"] {
    border-left-color: #14b8a6 !important;
    color: #14b8a6 !important;
    font-style: italic;
    background-color: #042f2e !important;
}

/* Dashboard Side Panel design styling */
.dashboard-panel {
    background-color: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    padding: 16px !important;
}

.primary-btn {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    border: none !important;
    font-weight: bold !important;
    color: white !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    transition: all 0.2s ease !important;
}

.primary-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
}
"""

with gr.Blocks(css=terminal_css, theme=gr.themes.Default()) as demo:
    # App Title Banner
    gr.HTML("<div id='terminal-header'>⚡ AGENTIC BOOK CLUB // IRC INTERACTION NODE ⚡</div>")
    
    with gr.Row():
        # Left Panel - 70% width for terminal log
        with gr.Column(scale=7):
            chatbot = gr.Chatbot(
                label="📁 #bookclub-lounge Log (Live Feed)", 
                type="messages", 
                elem_id="irc-log"
            )
            
        # Right Panel - 30% width for system controls & metrics
        with gr.Column(scale=3, elem_classes="dashboard-panel"):
            gr.Markdown("### ⚙️ SYSTEM CONTROL PANEL")
            
            # Active agents tracker
            active_agents_display = gr.Textbox(
                label="👥 Connected Autonomous Nodes",
                value="No agents currently online",
                interactive=False
            )
            
            # Orchestrator Launch Actions
            launch_btn = gr.Button(
                "🚀 Launch Cluster Session", 
                variant="primary", 
                elem_classes="primary-btn"
            )
            
            status_output = gr.Textbox(
                label="🛰️ Hub Orchestrator Status", 
                interactive=False, 
                placeholder="Awaiting connection..."
            )
            
            gr.Markdown(
                "**Operator Instructions:**\n"
                "1. Click the launcher button to wake the distributed orchestrator.\n"
                "2. System will instantiate dedicated Modal GPU environments.\n"
                "3. Autonomous nodes will connect automatically via local handshakes."
            )

    def sync_ui_state():
        """Updates the chat interface and connected agents counter simultaneously."""
        connected_list = list(ACTIVE_AGENTS)
        agents_text = ", ".join(connected_list) if connected_list else "No agents currently online"
        return GLOBAL_CHANNEL_LOG, agents_text

    # Bind active functions
    launch_btn.click(fn=run_modal_orchestrator, outputs=status_output)
    
    # Poll backend memory every 1.0 seconds to keep live feed sync'd
    timer = gr.Timer(1.0)
    timer.tick(sync_ui_state, outputs=[chatbot, active_agents_display])

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
