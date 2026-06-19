import os
import datetime
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# --- GLOBAL STATE CHANNEL BUS ---
GLOBAL_CHANNEL_LOG = [
    {
        "role": "assistant", 
        "content": "⚡ [SYSTEM] IRC Server Online. Port 7860 active. Waiting for orchestrator..."
    }
]

ACTIVE_AGENTS = set()

class Message(BaseModel):
    agent_id: str
    text: str

# --- API SOCKET ENDPOINTS ---

@app.post("/agent_join_channel")
async def join(agent_id: str):
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
    return GLOBAL_CHANNEL_LOG

@app.post("/agent_post_message")
async def post(msg: Message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    # Fix: Keep role as 'user' for Gradio compatibility, format the identifier directly into the text content
    entry = {
        "role": "user", 
        "content": f"[{timestamp}] <{msg.agent_id}> {msg.text}"
    }
    GLOBAL_CHANNEL_LOG.append(entry)
    ACTIVE_AGENTS.add(msg.agent_id)
    return {"status": "posted"}

def run_modal_orchestrator():
    """Triggers the single Modal aquarium container from the UI button click."""
    try:
        import modal
        
        # 1. Dynamically lookup your named Modal application
        # (Matches the app = modal.App("agentic-book-club-aquarium") name)
        try:
            f = modal.Function.from_name("agentic-book-club-aquarium", "trigger_host_node")
        except Exception:
            return "Error: Could not find deployed Modal function. Did you run 'modal deploy main.py' first?"

        # 2. Determine your current server URL
        irc_server_url = os.environ.get("IRC_SERVER_URL", "https://lumosgolem-agents-book-club.hf.space")

        # 3. Fire-and-forget spawn invocation so the Gradio UI doesn't freeze 
        # while waiting 1-2 minutes for the agents to finish talking.
        f.spawn(irc_url=irc_server_url)
        
        return "Aquarium container triggered! The Host is opening the room now..."
        
    except Exception as e:
        return f"Failed to trigger Modal container: {str(e)}"

# --- UI DESIGN SHELL ---
terminal_css = """
body, .gradio-container {
    background-color: #060913 !important;
    font-family: 'Courier New', Courier, monospace !important;
}
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
#irc-log {
    background-color: #02040a !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    padding: 12px !important;
    height: 520px !important;
}
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
}
"""

with gr.Blocks(css=terminal_css, theme=gr.themes.Default()) as demo:
    gr.HTML("<div id='terminal-header'>⚡ AGENTIC BOOK CLUB // IRC INTERACTION NODE ⚡</div>")
    
    with gr.Row():
        with gr.Column(scale=7):
            chatbot = gr.Chatbot(
                label="📁 #bookclub-lounge Log (Live Feed)", 
                type="messages", 
                elem_id="irc-log"
            )
            
        with gr.Column(scale=3, elem_classes="dashboard-panel"):
            gr.Markdown("### ⚙️ SYSTEM CONTROL PANEL")
            
            active_agents_display = gr.Textbox(
                label="👥 Connected Autonomous Nodes",
                value="No agents currently online",
                interactive=False
            )
            
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
        connected_list = list(ACTIVE_AGENTS)
        agents_text = ", ".join(connected_list) if connected_list else "No agents currently online"
        return GLOBAL_CHANNEL_LOG, agents_text

    launch_btn.click(fn=run_modal_orchestrator, outputs=status_output)
    
    timer = gr.Timer(1.0)
    timer.tick(sync_ui_state, outputs=[chatbot, active_agents_display])


app = gr.mount_gradio_app(app, demo, path="/ui")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)