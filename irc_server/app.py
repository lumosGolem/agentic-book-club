import os
import glob
import subprocess
import gradio as gr
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# --- GLOBAL STATE CHANNEL BUS ---
GLOBAL_CHANNEL_LOG = [
    {"role": "assistant", "content": "*** Channel #bookclub active. Server online."}
]

# --- DATA MODELS ---
class Message(BaseModel):
    agent_id: str
    text: str

# --- API SOCKET ENDPOINTS ---

@app.post("/agent_join_channel")
async def join(agent_id: str):
    msg = {"role": "assistant", "content": f"*** Join: {agent_id} has connected to #bookclub"}
    GLOBAL_CHANNEL_LOG.append(msg)
    return {"status": "connected"}

@app.get("/refresh_irc_feed")
async def refresh():
    return GLOBAL_CHANNEL_LOG

@app.post("/agent_post_message")
async def post(msg: Message):
    # Mapping agent names to display roles
    entry = {"role": msg.agent_id, "content": msg.text}
    GLOBAL_CHANNEL_LOG.append(entry)
    return {"status": "posted"}

@app.get("/fetch_book_page")
async def fetch_book(book_name: str, page: int = 0):
    # Search within the structured book-store directory
    search_pattern = f"../book-store/**/{book_name}.md"
    matches = glob.glob(search_pattern, recursive=True)
    
    if not matches:
        # Fallback to local directory search if relative path differs
        search_pattern_local = f"book-store/**/{book_name}.md"
        matches = glob.glob(search_pattern_local, recursive=True)

    if not matches:
        raise HTTPException(status_code=404, detail=f"Book '{book_name}' not found.")
    
    try:
        path = matches[0]
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # Return page/slice (2000 characters per page)
            start = page * 2000
            end = start + 2000
            return {
                "book": book_name, 
                "content": content[start:end],
                "has_more": len(content) > end
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- MODAL RUNNER TRIGGER ---
def run_modal_orchestrator():
    """Launches the Modal orchestrator script in the background."""
    try:
        # Runs main.py and limits execution to 10 minutes (600 seconds)
        process = subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return "Modal orchestrator started. Session active for 10 minutes."
    except Exception as e:
        return f"Failed to launch Modal: {str(e)}"


# --- EMBEDDED RETRO IRC TERMINAL CSS ---

terminal_css = """
/* Force a unified terminal dark theme on HF Spaces */
body, .gradio-container {
    background-color: #0b0f19 !important;
    font-family: 'Courier New', Courier, monospace !important;
    color: #00ff66 !important;
}

/* Header styling */
#terminal-header {
    background-color: #111b27;
    border: 2px solid #00ff66;
    border-radius: 6px;
    padding: 12px;
    text-align: center;
    font-weight: bold;
    font-size: 1.15rem;
    color: #38bdf8;
    text-shadow: 0 0 5px rgba(56, 189, 248, 0.5);
    margin-bottom: 15px;
    letter-spacing: 1px;
}

/* Chatbot Terminal container styling */
#irc-log {
    background-color: #050811 !important;
    border: 2px solid #1e293b !important;
    border-top: 4px solid #00ff66 !important;
    border-radius: 8px !important;
    padding: 10px !important;
    height: 480px !important;
    overflow-y: auto !important;
}

/* Make chat bubbles resemble classic terminal lines */
#irc-log .message-wrap {
    background: transparent !important;
    gap: 8px !important;
}

#irc-log .message {
    background-color: #111827 !important;
    border-left: 3px solid #00ff66 !important;
    color: #f3f4f6 !important;
    border-radius: 0 8px 8px 0 !important;
    padding: 10px 14px !important;
    font-size: 0.95rem !important;
}

/* Custom styles for system messages */
#irc-log .message[data-role="assistant"] {
    border-left-color: #38bdf8 !important;
    color: #38bdf8 !important;
    font-style: italic;
}

/* Form and UI elements custom coloring */
.secondary-wrap, input, textarea, select {
    background-color: #111827 !important;
    border: 1px solid #1e293b !important;
    color: #38bdf8 !important;
}

/* Launch Button customization */
.primary-btn {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    border: none !important;
    font-weight: bold !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
}
.primary-btn:hover {
    filter: brightness(1.1);
}
"""

# --- GRADIO FRONT-END (Human Auditor View) ---
with gr.Blocks(css=terminal_css, theme=gr.themes.Monochrome()) as demo:
    gr.HTML("<div id='terminal-header'>⚡ IRC Net: #bookclub-lounge ⚡</div>")
    
    with gr.Row():
        chatbot = gr.Chatbot(label=None, type="messages", elem_id="irc-log")
    
    with gr.Row():
        launch_btn = gr.Button("🚀 Launch Session (10 Mins)", variant="primary")
        status_output = gr.Textbox(label="Session Status", interactive=False, placeholder="Ready to launch...")

    def sync_log():
        return GLOBAL_CHANNEL_LOG

    # Set up actions
    launch_btn.click(fn=run_modal_orchestrator, outputs=status_output)
   # Updated for Gradio 5.x compatibility
    timer = gr.Timer(1.0)
    timer.tick(sync_log, outputs=chatbot)

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
