.agentic-book-club
|
├── README.md
├── book_store
│   ├── __init__.py
│   └── books
│       ├── BramStoker
│       │   └── Dracula.md
│       ├── MarcusAurelius
│       │   └── theMeditations.md
│       └── WilliamShakespeare
│           ├── RomeoJuliet
│           │   ├── Chapter_1.md
│           │   ├── Chapter_2.md
│           │   ├── Chapter_3.md
│           │   ├── Chapter_4.md
│           │   └── Chapter_5.md
│           └── RomeoJuliet.md
├── club_members
│   ├── __init__.py
│   ├── member_one
│   │   ├── __init__.py
│   │   ├── agent.py                                # Kai >> Club Member >> "gemma-4-12B-it" 
│   │   ├── assets
│   │   │   └── WilliamShakespeare
│   │   ├── prompts
│   │   │   ├── __init__.py
│   │   │   └── prompts.py
│   │   ├── skills
│   │   │   ├── __init__.py
│   │   │   ├── book_summary_skill
│   │   │   │   ├── SKILL.md
│   │   │   │   └── __init__.py
│   │   │   └── irc_skill
│   │   │       ├── SKILL.MD
│   │   │       └── __init__.py
│   │   ├── tools
│   │   │   ├── __init__.py
│   │   │   └── tools.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── utils.py
│   ├── member_three
│   │   ├── __init__.py
│   │   ├── agent.py                            # Mack >> Club Member >> "gemini-2.5-flash"
│   │   ├── assets
│   │   │   └── WilliamShakespeare
│   │   ├── prompts
│   │   │   ├── __init__.py
│   │   │   └── prompts.py
│   │   ├── skills
│   │   │   ├── __init__.py
│   │   │   ├── book_summary_skill
│   │   │   │   ├── SKILL.md
│   │   │   │   └── __init__.py
│   │   │   └── irc_skill
│   │   │       ├── SKILL.MD
│   │   │       └── __init__.py
│   │   ├── tools
│   │   │   ├── __init__.py
│   │   │   └── tools.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── utils.py
│   └── member_two
│       ├── __init__.py
│       ├── agent.py                       # River >> Club Host >> "gemini-2.5-flash" 
│       ├── prompts
│       │   ├── __init__.py
│       │   └── prompts.py
│       ├── skills
│       │   ├── __init__.py
│       │   └── club_host_skill
│       │       ├── SKILL.md
│       │       └── __init__.py
│       ├── tools
│       │   ├── __init__.py
│       │   └── tools.py
│       └── utils
│           ├── __init__.py
│           └── utils.py
├── design-faq
│   ├── agent2server-discovery.md
│   ├── dir_structure.md
│   ├── how_to_run.md
│   ├── project_pitch.md
│   └── solution_draft.md
├── dir_tree.md
├── irc_server
│   ├── app.py
│   └── irc_server_readme.md
├── main.py
└── requirements.txt

37 directories, 65 files
