# agentic_book_club
A book club for agents

## dir structure

```
root::SmallLangModels/
├── design_faq/                     # Docs for System Architecture, Dir structure, Project pitch..
├── README.md
|                
├── IRC_server/
│   ├── app.py                      # Central Gradio/FastAPI Passive Server Engine
│   └── irc_server_readme.md        # IRC level readme
|   └──  __init__.py
|
|
├── book-store/
|    ├── books/
|    │   └── WilliamShakespear/RomeoJuliet.md      # Target book assets (Open-source Markdown)
|    │   └── BramStoker/Dracula.md                 # Target book assets (Open-source Markdown)
|    │   └── MarcusAurelius/theMeditations.md      # Optional book assets (Open-source Markdown)
|        └──  __init__.py
|    ├── tools
|        └── tools.py
|    ├── book-case                                   #storage
|        └── index.faiss
|    ├── engine.py                                   #Rag engine
|    └──  __init__.py
├── members/
|    ├── member_one/
|        ├── __init__.py         # init
|        ├── agent.py            # ADK agent for Member 1
|        ├── prompts/
|        │   └── prompts.md      # Prompt template > Personality matrix
|        ├── skills/
|        │   └── skills.md       # SKILL.md ;  book club ethiquet
|        ├── tools/
|        │   └── tools.py        # i.e def functions re Server REST API, bookclub tools.
|        └── utils/
|            └── utils.py        # i.e. prompt builder
|            └── hf_loader.py    # a local Hub ingestion wrapper 
|   
|    ├── member_two/
|        ├── __init__.py         # init
|        ├── agent.py            # ADK agent for Member 2
|        ├── prompts/
|        │   └── prompts.md      # Prompt template > Personality matrix
|        ├── skills/
|        │   └── skills.md       # SKILL.md ;  book club ethiquet
|        ├── tools/
|        │   └── tools.py        # i.e def functions re Server REST API, bookclub tools.
|        └── utils/
|            └── utils.py        # i.e. prompt builder
|            └── hf_loader.py    # a local Hub ingestion wrapper 
|    │
|    └── member_three/
|        ├── __init__.py         # init
|        ├── agent.py            # ADK agent for Member 3
|        ├── prompts/
|        │   └── prompts.md      # Prompt template > Personality matrix
|        ├── skills/
|        │   └── skills.md       # SKILL.md ;  book club ethiquet
|        ├── tools/
|        │   └── tools.py        # i.e def functions re Server REST API, bookclub tools.
|        └── utils/
|            └── utils.py        # i.e. prompt builder
|            └── hf_loader.py    # a local Hub ingestion wrapper
 

```

