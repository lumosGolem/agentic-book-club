import os
import asyncio
import logging
#from pathlib import Path
from contextlib import AsyncExitStack

# ADK 2.0 Core Importsh
from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.models.google_llm import Gemini

# Local Book Club Assets
from .tools.tools import get_bookclub_tools
from dotenv import load_dotenv
from .utils.hf_loader import GemmaInferenceEngine # Local model wrapper
from .prompts.prompts import KAI_INSTRUCTION #adk2 prompt template

logging.basicConfig(level=logging.ERROR)
load_dotenv()

# --- CONFIGURATION ---
AGENT_NAME = "Kai"
MODEL_ID = "google/gemma-4-12B-it" 
GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")
pseudo_model_name = "gemini-2.5-flash"

async def initialize_bookclub_agent():
    local_engine = GemmaInferenceEngine(model_name=MODEL_ID)
    shared_exit_stack = AsyncExitStack()

    agent = Agent(
        name="Kai",
        model=pseudo_model_name, 
        description="A member of the Agents' Book Club. Name is Kai",
        instruction=KAI_INSTRUCTION,
        tools=get_bookclub_tools(shared_exit_stack),         
        planner=PlanReActPlanner() 
    )

    async def local_call_override(prompt: str, **kwargs):
        return local_engine.generate(prompt)

    #agent.local_engine = local_engine
    agent._call_model = local_call_override  

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
