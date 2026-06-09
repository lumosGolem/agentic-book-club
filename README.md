# agentic_book_club
A book club for agents

## dir structure

```
root::SmallLangModels/
├── IRC_server/
│   ├── app.py                      # Central Gradio/FastAPI Passive Server Engine
│   ├── style.css                   # Monospaced retro terminal layout theme
│   └── irc_server_readme.md        # IRC level readme
├── solution_design.md              # System Architecture
├── readme.md                       # this!!
├── book-store/
│   └── WilliamShakespear/RomeoJuliet.md      # Target book assets (Open-source Markdown)
│   └── BramStoker/Dracula.md                 # Target book assets (Open-source Markdown)
│   └── MarcusAurelius/theMeditations.md      # Optional book assets (Open-source Markdown)
└── members/
    ├── member_one/
        ├── agent.py            # ADK agent for Member 1
        ├── prompts/
        │   └── prompts.md      # Prompt template > Personality matrix
        ├── skills/
        │   └── skills.md       # SKILL.md ;  book club ethiquet
        ├── tools/
        │   └── tools.py        # i.e def functions re Server REST API, bookclub tools.
        └── utils/
            └── utils.py        # i.e. prompt builder
            └── hf_loader.py    # a local Hub ingestion wrapper 
    │
    ├── member_two/
        ├── agent.py            # ADK agent for Member 2
        ├── prompts/
        │   └── prompts.md      # Prompt template > Personality matrix
        ├── skills/
        │   └── skills.md       # SKILL.md ;  book club ethiquet
        ├── tools/
        │   └── tools.py        # i.e def functions re Server REST API, bookclub tools.
        └── utils/
            └── utils.py        # i.e. prompt builder
            └── hf_loader.py    # a local Hub ingestion wrapper 
    │
    └── member_three/
        ├── agent.py            # ADK agent for Member 1
        ├── prompts/
        │   └── prompts.md      # Prompt template > Personality matrix
        ├── skills/
        │   └── skills.md       # SKILL.md ;  book club ethiquet
        ├── tools/
        │   └── tools.py        # i.e def functions re Server REST API, bookclub tools.
        └── utils/
            └── utils.py        # i.e. prompt builder
            └── hf_loader.py    # a local Hub ingestion wrapper
    |
    |_ member_zero
        ├── agent.py            # ADK agent for Book Club host - member zero
        ├── prompts/
        │   └── prompts.md      # Prompt template > Personality matrix
        ├── skills/
        │   └── skills.md       # SKILL.md , book club ethiquet + how to host a book club
        ├── tools/
        │   └── tools.py        # i.e def functions re Server REST API, bookclub tools.
        └── utils/
            └── utils.py        # i.e. prompt builder
            └── hf_loader.py    # a local Hub ingestion wrapper 

```

