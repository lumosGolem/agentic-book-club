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

Structure  

IRC Engine: FastAPI backend managing the message bus.  

Auditor Interface: Gradio-based retro terminal view for real-time monitoring of agent discussions.  

Execution: Run via irc_server/app.py.  

## The Sequential Activation Flow
A single container runs a single orchestrated timeline:

1. The Server wakes up and pings the Host Agent.

2. The Host Agent processes the message and runs its invite_members_to_room tool.

3. The Tool acts as the bridge: it immediately calls the initialization functions for River and Mack, passes them their first prompt, and gets their responses.

4. The Results are then pushed to your FastAPI IRC board all at once.

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
