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
from .utils.utils import PromptBuilder  
from .utils.hf_loader import GemmaInferenceEngine # Local model wrapper
from .prompts.prompts import KAI_INSTRUCTION #adk2 prompt template

logging.basicConfig(level=logging.ERROR)

# --- CONFIGURATION ---
AGENT_NAME = "Kai"
MODEL_ID = "google/gemma-4-12B-it" 

async def initialize_bookclub_agent():
    """
    Initializes agent-Kai.
    Orchestrates tools and loads the local model via HF.
    """
    # 1. Setup Tools
    # Shared exit stack manages the lifecycle of HTTP connections to the IRC server
    shared_exit_stack = AsyncExitStack()    
    bookclub_tools = get_bookclub_tools(shared_exit_stack)

    # 2. Instantiate the Local Inference Engine (Loads weights onto GPU memory)
    # This ensures heavy weight-loading is kept inside the deferred initialization.
    local_engine = GemmaInferenceEngine(model_id=MODEL_ID)

    # 3. Return the ADK Agent instance configured to route through the local engine
    agent = Agent(
        name=AGENT_NAME,
        model=MODEL_ID,
        description="A member of the Agents' Book Club. Name is Kai",
        instruction=KAI_INSTRUCTION,
        tools=bookclub_tools, 
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True, 
                thinking_budget=512,   
            )
        ),
        generate_content_config=types.GenerateContentConfig(
            temperature=0.75, 
            max_output_tokens=150,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    initial_delay=2,
                    attempts=3
                )
            )
        )
    )
    
    # Bind the instantiated local GPU engine instance to the agent
    agent.local_engine = local_engine
    return agent

class DeferredInitializationAgent(Agent):
    """
    ADK 2.0 Wrapper: Defers the model weight loading 
    until the first async request is made.
    """
    def __init__(self, name: str, initialization_coro_func):
        # Initialize with placeholder model and empty tools for immediate registration
        super().__init__(name=name, model="placeholder/loading", tools=[])
        
        object.__setattr__(self, 'version', '1.0.0')
        self._initialization_coro_func = initialization_coro_func
        self._initialized_agent_delegate = None
        self._is_fully_initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_initialized(self):
        """Triggers the HF loader and ADK Agent setup."""
        async with self._init_lock:
            if not self._is_fully_initialized:
                # This call launches initialize_bookclub_agent()
                self._initialized_agent_delegate = await self._initialization_coro_func()
        
                # Map initialized attributes to the wrapper
                self.model = self._initialized_agent_delegate.model
                self.description = self._initialized_agent_delegate.description
                self.instruction = self._initialized_agent_delegate.instruction
                self.tools = self._initialized_agent_delegate.tools
                
                # Expose local engine to the wrapper
                self.local_engine = getattr(self._initialized_agent_delegate, 'local_engine', None)
                
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
        
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
#            --- EXPORTED ROOT AGENT ---                                            #######################################
# This instance is what the main.py will register in the Book Club orchestration.   #######################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
root_agent = DeferredInitializationAgent(
    name=AGENT_NAME, 
    initialization_coro_func=initialize_bookclub_agent
)

async def get_root_agent():
    """Helper to ensure full readiness before the Book Club begins."""
    if isinstance(root_agent, DeferredInitializationAgent):
        await root_agent._ensure_initialized()
    return root_agent
