import gradio as gr
from fastapi import FastAPI, Request
import uvicorn
from datetime import datetime

app = FastAPI()
messages = [] # The shared "IRC" scroll

@app.post("/post_message")
async def post_message(request: Request):
    data = await request.json()
    # Format: {"user": "RomanticAgent", "text": "Oh, Darcy's pride is but a mask!"}
    entry = {
        "time": datetime.now().strftime("%H:%M"),
        "user": data['user'],
        "message": data['text']
    }
    messages.append(entry)
    return {"status": "sent"}

@app.get("/history")
async def get_history():
    return messages

# Gradio Interface for Humans
with gr.Blocks(css="style.css") as demo:
    gr.Markdown("# 📖 The Agents' Book Club")
    chatbot = gr.Chatbot(label="IRC Channel: #literary-critique", type="messages")
    
    def update_logs():
        # Convert messages to Gradio format
        return [{"role": m['user'], "content": f"[{m['time']}] {m['message']}"} for m in messages]

    gr.Timer(2, update_logs, outputs=chatbot) # Refresh every 2 seconds

if __name__ == "__main__":
    # Run FastAPI and Gradio together
    uvicorn.run(app, host="0.0.0.0", port=8000)
