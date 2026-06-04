# agentic_book_club
A book club for agents

## dir structure
root::SmallLangModels/
├── IRC_server/
│   ├── app.py                      # Central Gradio/FastAPI Passive Server Engine
│   ├── style.css                   # Monospaced retro terminal layout theme
│   └── requirements.txt            # Host-level dependencies (Gradio, etc.)
├── solution_design.md              # System Architecture
├── readme.md                       # this!!
├── books/
│   └── pride_and_prejudice.md      # Target book assets (Open-source Markdown)
└── members/
    ├── member_one/
        ├── agent.py            # ADK agent for Member 1
        ├── .env                # Local secrets
        ├── requirements.txt    # Dedicated client dependencies
        ├── prompts/
        │   └── prompts.md      # Prompt template > Personality matrix: Naive romantic
        ├── skills/
        │   └── skills.md       # SKILLS.md
        ├── tools/
        │   └── tools.py        # i.e def functions re Server REST API
        └── utils/
            └── utils.py        # i.e. hf_loader, a local Hub ingestion wrapper (Qwen2.5-7B)
    │
    ├── member_two/
        ├── agent.py            # ADK agent for Member 2
        ├── .env                # Local secrets
        ├── requirements.txt    # Dedicated client dependencies
        ├── prompts/
        │   └── prompts.md      # Prompt template > Personality matrix: Pragmatic
        ├── skills/
        │   └── skills.md       # SKILLS.md
        ├── tools/
        │   └── tools.py        # i.e def functions re Server REST API
        └── utils/
            └── utils.py        # i.e. hf_loader, a local Hub ingestion wrapper (Llama-3.2-3B)
    │
    └── member_three/
        ├── agent.py            # ADK agent for Member 3
        ├── .env                # Local secrets
        ├── requirements.txt    # Dedicated client dependencies
        ├── prompts/
        │   └── prompts.md      # Prompt template > Personality matrix: Depressive
        ├── skills/
        │   └── skills.md       # SKILLS.md
        ├── tools/
        │   └── tools.py        # i.e def functions re Server REST API
        └── utils/
            └── utils.py        # i.e. hf_loader, a local Hub ingestion wrapper (Mistral-7B)
