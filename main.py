import os
import asyncio
import modal

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

# 1. Image Pre-download Hook (Pre-bakes the embedding model into the container disk)
def download_rag_embeddings():
    from sentence_transformers import SentenceTransformer
    print("--- [IMAGE BUILD] Baking all-MiniLM-L6-v2 into container disk ---")
    SentenceTransformer("all-MiniLM-L6-v2")

# Define the Modal Image (The Runtime Environment)
image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install(
        "google-adk>=2.2.0", 
        "httpx", 
        "transformers", 
        "bitsandbytes", 
        "accelerate", 
        "torch", 
        "sentencepiece",
        "gradio-client",

        "sentence-transformers",  # Required for RAG embedding engine
        "faiss-cpu"                # cpu FAISS vector database
    )
    .run_function(download_rag_embeddings) # Pre-caches the 90MB weights
)

app = modal.App("book-club")

# Secret Management (Hugging Face tokens for model access, IRC URLs)
HF_TOKEN = modal.Secret.from_name("huggingface-secret") 
IRC_SERVER_URL = modal.Secret.from_name("IRC_SERVER_URL")
GEMINI_API_KEY=modal.Secret.from_name("GEMINI_API_TOKEN")

# Configure directory mounts so local code is visible inside the container
local_code_mount = modal.mount.from_local_dir(".", remote_path="/root")

##offloading weights

MODEL_CACHE = {}

def load_model(model_id: str):

    if model_id in MODEL_CACHE:
        return MODEL_CACHE[model_id]

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
    )

    MODEL_CACHE[model_id] = (model, tokenizer)

    return model, tokenizer



# 2. The Agent Runner (The "Client Node" Execution)
@app.function(
    image=image,
    secrets=[HF_TOKEN, IRC_SERVER_URL,GEMINI_API_KEY],
    gpu="A10G",               # High-performance GPU for quantized 12B/14B models
    timeout=3600,             # 1 hour limit for active club sessions
    container_idle_timeout=300,
    mounts=[local_code_mount]
)

async def run_agent_session(member_id: str, session_name: str, irc_url: str):
    """
    Runs an individual agent's lifecycle loop entirely inside a Modal GPU node.
    This resolves serialization issues by importing and initializing the agent 
    directly within the target execution environment.
    """
    print(f"--- [SYSTEM] Remote Node Initialized. Booting {member_id} ({session_name}) ---")
    
    # Propagate the Hugging Face Space URL so the tools can reach it
    os.environ["IRC_SERVER_URL"] = irc_url
    
    # Force sentence-transformers to use the baked-in disk cache directly
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    
    # Dynamic runtime import prevents local non-GPU imports from raising errors
    # (Matches your 'members/' folder path naming convention)
    if member_id == "member_one":
        from club_members.member_one.agent import root_agent as agent_instance
    elif member_id == "member_two":
        from club_members.member_two.agent import root_agent as agent_instance
    elif member_id == "member_three":
        from club_members.member_three.agent import root_agent as agent_instance
    else:
        raise ValueError(f"Unknown agent member identifier: {member_id}")

    # Trigger the 'Deferred' loading of model weights on CUDA
    # This will also trigger the shared book-store RAG initialization once
    await agent_instance._ensure_initialized()
    
    print(f"--- [SYSTEM] {agent_instance.name} Model Loaded & Handshake complete. Entering IRC Loop ---")
    
    # Active simulation loop
    while True:
        try:
            # We use process_request to trigger the ADK agent logic
            # This triggers observation, reasoning, tool execution, and communication back to HF
            response = await agent_instance.process_request(
                "Read the latest book club channel messages. If a book club discussion is active, share your unique perspective."
            )
            print(f"[{agent_instance.name} Response Generated]: {response.text}")
            
            # Cooperative delay: Prevent agents from overwhelming the IRC feed instantly
            await asyncio.sleep(20) 
            
        except Exception as e:
            print(f"Error in {agent_instance.name} remote execution loop: {e}")
            await asyncio.sleep(30)

# 3. The Main Orchestrator (Local Entrypoint)
@app.local_entrypoint()
def main():
    """
    Launches all independent agent instances simultaneously on separate Modal GPU containers.
    """
    # Fetch public space environment URL or fall back to localhost
    irc_server_url = os.environ.get("IRC_SERVER_URL", "https://lumosgolem-agents-book-club.hf.space")
    
    print("--- 📖 WELCOME TO THE DISTRIBUTED AGENTS' BOOK CLUB ---")
    print(f"Connecting observer nodes to IRC Hub: {irc_server_url}")
    print("Spinning up remote GPU container clusters for independent brains...")
    
    # Define agent assignments and their directories
    agent_mappings = [
        ("member_one", "Kai"),
        ("member_two", "River"),
        ("member_three", "Mack"),
    ]
    
    # Run the virtual aquarium parallel tasks
    with app.run():
        futures = []
        for member_id, description in agent_mappings:
            print(f"Deploying {description} to active GPU instance...")
            fut = run_agent_session.spawn(member_id, description, irc_server_url)
            futures.append(fut)
            
        print("--- [SYSTEM] All distributed agents launched. Observing feed live ---")
        
        # Keep the entrypoint parent process alive while children discuss
        for future in futures:
            future.get()


@modal.fastapi_endpoint(method="POST")
def generate(data: dict):

    MODEL_MAP = {
        "google/gemma-4-12b-it": "google/gemma-4-12b-it",
    }

    model_key = data["model"]

    model_id = MODEL_MAP[model_key]

    prompt = data["prompt"]

    max_tokens = data.get("max_tokens", 150)

    model, tokenizer = load_model(model_id)

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    ).to("cuda")

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            do_sample=True,
        )

    response = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    return {
        "response": response
    }