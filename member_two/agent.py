import os
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
from .utils.hf_loader import QwenInferenceEngine  
from .prompts.prompts import RIVER_INSTRUCTION 

logging.basicConfig(level=logging.ERROR)

# --- CONFIGURATION ---
AGENT_NAME = "River_Member2"
MODEL_ID = "Qwen/Qwen3-14B" 

async def initialize_bookclub_agent():
    """
    Initializes River.
    Orchestrates tools and boots the local quantized HF engine safely.
    """
    # 1. Setup Tools
    shared_exit_stack = AsyncExitStack()    
    bookclub_tools = get_bookclub_tools(shared_exit_stack)

    # 2. Instantiate the Local HF Engine
    local_engine = QwenInferenceEngine(model_id=MODEL_ID)

    # 3. Create ADK Agent Instance
    base_agent = Agent(
        name=AGENT_NAME,
        model=MODEL_ID,
        description="A member of the Agents' Book Club with a pragmatic perspective.",
        instruction=RIVER_INSTRUCTION,
        tools=bookclub_tools,         
        planner=BuiltInPlanner(),
        generate_content_config=types.GenerateContentConfig(
            temperature=0.75,
            max_output_tokens=150,
        )
    )
    
    # Expose the local engine as an attribute so the wrapper can bypass API calls
    setattr(base_agent, "local_engine", local_engine)
    return base_agent

class DeferredInitializationAgent(Agent):
    """
    ADK 2.0 Wrapper: Defers local model weight loading until the first async call,
    and intercepts execution to run inference locally instead of calling external APIs.
    """
    def __init__(self, name: str, initialization_coro_func):
        super().__init__(name=name, model="placeholder/loading", tools=[])
        
        object.__setattr__(self, 'version', '1.0.0')
        self._initialization_coro_func = initialization_coro_func
        self._initialized_agent_delegate = None
        self._is_fully_initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_initialized(self):
        """Triggers the heavy HF loader loading sequence securely via lock."""
        async with self._init_lock:
            if not self._is_fully_initialized:
                self._initialized_agent_delegate = await self._initialization_coro_func()
        
                self.model = self._initialized_agent_delegate.model
                self.description = self._initialized_agent_delegate.description
                self.instruction = self._initialized_agent_delegate.instruction
                self.tools = self._initialized_agent_delegate.tools
                
                object.__setattr__(self, 'version', getattr(self._initialized_agent_delegate, 'version', '1.0.0'))
                self._is_fully_initialized = True

    async def run_async(self, invocation_context):
        """Intercepts streaming workflows for local generation processing."""
        await self._ensure_initialized()
        # Fallback tracking if tools or context streams are passed directly
        async for event in self._initialized_agent_delegate.run_async(invocation_context):
            yield event

    async def process_request(self, request, invocation_context=None, tools_code_execution_config=None):
        """
        Intercepts incoming messages and prepares a structurally sound
        ChatML payload using Qwen's native token rules.
        """
        await self._ensure_initialized()

        user_content = request.new_message.parts[0].text if hasattr(request, 'new_message') else str(request)
        
        # Structure the payload into standard role dictionaries
        messages = [
            {
                "role": "system", 
                "content": self.instruction
            },
            {
                "role": "user", 
                "content": f"Current Book Club Context:\n{user_content}\n\nWhat is your response to the club?"
            }
        ]
        
        # 3. Apply the official chat template
        full_prompt = self._initialized_agent_delegate.local_engine.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True  
        )
        
        # 4. Route logic through your customized local engine instance
        local_response = self._initialized_agent_delegate.local_engine.generate(
            prompt=full_prompt, 
            max_tokens=150
        )
        
        return local_response

###################################################
###################################################
#          --- EXPORTED ROOT AGENT ---            #
###################################################
###################################################
root_agent = DeferredInitializationAgent(
    name=AGENT_NAME, 
    initialization_coro_func=initialize_bookclub_agent
)

async def get_root_agent():
    if isinstance(root_agent, DeferredInitializationAgent):
        await root_agent._ensure_initialized()
    return root_agent
