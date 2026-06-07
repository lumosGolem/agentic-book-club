import asyncio
import logging
from pathlib import Path
from contextlib import AsyncExitStack

# ADK 2.0 Core Imports
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types

# Local Book Club Assets
from .tools.tools import get_bookclub_tools
from .utils.hf_loader import get_gemma_model_config 

logging.basicConfig(level=logging.ERROR)

# --- CONFIGURATION ---
# pointing to Gemma 4 12B. In ADK 2.0, when using Hugging Face, 
# we often route through a local inference server or a custom HF-bridge.
AGENT_NAME = "Alex_Member1"
MODEL_ID = "google/gemma-4-12b" 

# Path to the specific persona for this member
PROMPT_PATH = Path(__file__).parent / "prompts" / "prompts.md"

async def initialize_bookclub_agent():
    """
    Initializes the Naive Romantic Agent.
    
    Instead of sub-agents, this agent focuses on two key toolsets:
    1. IRC_Tools: Communicating with the Gradio/FastAPI server.
    2. Library_Tools: Reading slices from the markdown books.
    """

    # 1. Setup Tools
    # We use the AsyncExitStack to manage the session with the IRC REST API
    shared_exit_stack = AsyncExitStack()    
    bookclub_tools = get_bookclub_tools(shared_exit_stack)

    # 2. Load Persona Instructions
    with open(PROMPT_PATH, "r") as f:
        persona_instructions = f.read()

    # 3. Return the ADK Agent
    return Agent(
        name=AGENT_NAME,
        model=MODEL_ID,
        description="A member of the Agents' Book Club with a naive, romantic perspective.",
        instruction=persona_instructions,
        tools=bookclub_tools, 

        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True, # We want to see the "Internal Monologue" in the ADK debug log
                thinking_budget=512,   # Gemma 4's reasoning budget
            )
        ),
        # Custom configuration for Hugging Face Inference
        generate_content_config=types.GenerateContentConfig(
            temperature=0.7, # Higher temperature for more "creative/romantic" flair
            max_output_tokens=150, # Keep IRC messages brief
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    initial_delay=2,
                    attempts=3
                )
            )
        )
    )

class DeferredInitializationAgent(Agent):
    """
    Handles the asynchronous loading of Gemma 4 12B.
    This ensures the Gradio UI can show the agent is 'Connecting...' 
    instead of freezing while the model weights load into GPU memory.
    """
    def __init__(self, name: str, initialization_coro_func):
        # Initialize with placeholder values for synchronous registration
        super().__init__(name=name, model="loading_gemma_4...", tools=[])
        
        object.__setattr__(self, 'version', '1.0.0')
        self._initialization_coro_func = initialization_coro_func
        self._initialized_agent_delegate = None
        self._is_fully_initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_initialized(self):
        async with self._init_lock:
            if not self._is_fully_initialized:
                # This is where the model weights actually load
                self._initialized_agent_delegate = await self._initialization_coro_func()
        
                self.model = self._initialized_agent_delegate.model
                self.description = self._initialized_agent_delegate.description
                self.instruction = self._initialized_agent_delegate.instruction
                self.tools = self._initialized_agent_delegate.tools
                
                object.__setattr__(self, 'version', getattr(self._initialized_agent_delegate, 'version', '1.0.0'))
                self._is_fully_initialized = True

    async def run_async(self, invocation_context):
        await self._ensure_initialized()
        async for event in self._initialized_agent_delegate.run_async(invocation_context):
            yield event

    async def process_request(self, request, invocation_context=None, tools_code_execution_config=None):
        await self._ensure_initialized()
        return await self._initialized_agent_delegate.process_request(
            request, invocation_context, tools_code_execution_config
        )


###################################
#    --- EXPORTED INSTANCE ---    #
###################################
# This is what main.py will import.
root_agent = DeferredInitializationAgent(
    name=AGENT_NAME, 
    initialization_coro_func=initialize_bookclub_agent
)

async def get_root_agent():
    if isinstance(root_agent, DeferredInitializationAgent):
        await root_agent._ensure_initialized()
    return root_agent
