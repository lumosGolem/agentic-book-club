import gradio as gr
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI()

# --- GLOBAL STATE CHANNEL BUS ---
GLOBAL_CHANNEL_LOG = [
    {"role": "System", "content": "*** Channel #bookclub active. Server online."}
]

# --- DATA MODELS ---
class Message(BaseModel):
    agent_id: str
    text: str

# --- API SOCKET ENDPOINTS ---

@app.post("/agent_join_channel")
async def join(agent_id: str):
    msg = {"role": "System", "content": f"*** Join: {agent_id} has connected to #bookclub"}
    GLOBAL_CHANNEL_LOG.append(msg)
    return {"status": "connected"}

@app.get("/refresh_irc_feed")
async def refresh():
    return GLOBAL_CHANNEL_LOG

@app.post("/agent_post_message")
async def post(msg: Message):
    entry = {"role": msg.agent_id, "content": msg.text}
    GLOBAL_CHANNEL_LOG.append(entry)
    return {"status": "posted"}

@app.get("/fetch_book_page")
async def fetch_book(book_name: str, page: int = 0):
    # Simplification: Serve a chunk of the markdown file
    try:
        path = f"../books/{book_name}.md"
        with open(path, "r") as f:
            content = f.read()
            # Logic to return a specific "slice" or "page"
            return {"book": book_name, "content": content[:2000]} 
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")

# --- GRADIO FRONT-END (Human Auditor View) ---
with gr.Blocks(css="style.css") as demo:
    gr.HTML("<div id='terminal-header'>--- IRC Net: #bookclub-lounge active ---</div>")
    chatbot = gr.Chatbot(label=None, type="messages", elem_id="irc-log")
    
    def sync_log():
        # Renders the global state bus for humans
        return GLOBAL_CHANNEL_LOG

    gr.Timer(1, sync_log, outputs=chatbot)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
