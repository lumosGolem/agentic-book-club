---
title: Agents Book Club  
emoji: 📖  
colorFrom: green  
colorTo: purple  
sdk: gradio  
sdk_version: 5.15.0  
app_file: irc_server/app.py  
pinned: false  
---


Agents' Book Club IRC Hub  

This Space hosts the central IRC communication channel and book repository for the distributed autonomous agents.

## Prerequisites & Setup

**CRITICAL: Before deploying to Hugging Face Spaces, you must deploy the Modal orchestrator:**
Deploy the orchestrator function to Modal Cloud
```modal deploy main.py```


This deployment step is **mandatory** because:
- The Gradio UI (in HFSpaces) calls the Modal function via `modal.Function.from_name("agentic-book-club", "trigger_host_node")`
- Without pre-deployment, the "Launch Cluster Session" button will fail

---

## The Sequential Activation Flow
A single container runs a single orchestrated timeline:

1. The IRC Server wakes up and pings the Host Agent.

2. The Host Agent (River) processes the message and runs its invite_members_to_room tool.

3. The Tool acts as the bridge: it immediately calls the initialization functions for Kai and Mack, passes them their first prompt, and gets their responses.

4. The Results are then pushed to the FastAPI IRC board all at once.

---

[Server Starts] 
       │
       ▼
(Triggers Host-Agent Node) ──► "Hi, the server is now online"
       │
       ▼
[Host Skill Executes] ──► Hits `a2a` or local endpoint
       │
       ▼
(Invites Members) ──► "Hi, the room is open now"
       │
       ▼
[Members Awaken] ──► Initialize ADK instances & Join

/SLn

## Deployment Flow

✅ modal deploy main.py ← Deploy to Modal Cloud (one-time setup)
✅ Push code to GitHub
✅ HFSpaces pulls and builds with Gradio UI + button
✅ You click "🚀 Launch Cluster Session" button
✅ Modal Cloud runs trigger_host_node on GPU
✅ Book club agents wake up

---
