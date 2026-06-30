import os
import asyncio
import logging
from pathlib import Path
from contextlib import AsyncExitStack

# ADK 2.0 Core Import
from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.models.google_llm import Gemini

# Local Book Club Assets
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
from .tools.tools import get_bookclub_tools
from .prompts.prompts import KAI_INSTRUCTION #adk2 prompt template

logging.basicConfig(level=logging.ERROR)

# --- CONFIGURATION ---
AGENT_NAME = "Kai"
MODEL_ID = "gemma-4-12B-it" 


# --- Skills ---

irc_skill = load_skill_from_dir(
    Path(__file__).parent / "skills" / "irc-etiquette"
)
book_summary_skill = load_skill_from_dir(
    Path(__file__).parent / "skills" / "book-summarisation"
)

shared_exit_stack = AsyncExitStack()
kai_toolset = get_bookclub_tools(shared_exit_stack)

kai_skill_toolset = skill_toolset.SkillToolset(
    skills=[irc_skill, book_summary_skill],
#   additional_tools=kai_toolset,
)
kai_skill_toolset = [kai_skill_toolset] + kai_toolset
# --- LLMAgent ---
async def initialize_bookclub_agent():
    MODEL_NAME = Gemini(model=MODEL_ID)

    agent = Agent(
        name=AGENT_NAME,
        model=MODEL_NAME, 
        description=f"A member of the Agents' Book Club. Name is {AGENT_NAME}",
        instruction=KAI_INSTRUCTION,
        tools= kai_skill_toolset,         
        planner=PlanReActPlanner() 
    )
    return agent, shared_exit_stack

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
        self._shared_exit_stack = None
        self._is_fully_initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_initialized(self):
        """ADK Agent setup."""
        async with self._init_lock:
            if not self._is_fully_initialized:
                # This call launches initialize_bookclub_agent()
                agent, shared_exit_stack =await self._initialization_coro_func()
                self._initialized_agent_delegate = agent
                self._shared_exit_stack = shared_exit_stack
        
                # Map initialized attributes to the wrapper
                self.model = agent.model
                self.description = agent.description
                self.instruction = agent.instruction
                self.tools = agent.tools
                self.planner = agent.planner
                                
                object.__setattr__(self, 'version', getattr(agent, 'version', '1.0.0'))
                self._is_fully_initialized = True

    async def run_async(self, invocation_context):
        await self._ensure_initialized()        
        async for event in self._initialized_agent_delegate.run_async(invocation_context):
            yield event

    async def process_request(self, request, invocation_context=None, tools_code_execution_config=None):
        """
        Executes the agent run via InMemoryRunner to capture the 
        final text response safely without low-level attribute crashes.
        """
        await self._ensure_initialized()        
        
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        
        # 1. Instantiate the runner to orchestrate the agent's event loop
        runner = InMemoryRunner(agent=self._initialized_agent_delegate)
        
        # 2. Create the session and let the database generate its own unique ID.
        # We store the resulting Session object which contains the generated id.
        session = await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id="operator"
        )
        
        # 3. Package the prompt text using Google's GenAI Content/Part schema
        input_content = types.Content(
            role="user",
            parts=[types.Part(text=request)]
        )
        
        final_text = ""
        
        # 4. Stream the runner execution asynchronously.
        # We pass session.id (the exact generated ID) to fulfill the 
        # required keyword-only argument constraint.
        async for event in runner.run_async(
            user_id="operator",
            session_id=session.id,  # Dynamically pass the exact generated ID
            new_message=input_content
        ):
            # 5. Capture the final output text of the agent run
            if event.is_final_response() and event.content is not None:
                final_text = "".join(
                    part.text for part in event.content.parts if getattr(part, "text", None)
                )
                
        return final_text
        
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
