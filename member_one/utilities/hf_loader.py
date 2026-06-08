import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

def get_gemma_model_config(model_id: str):
    """
    Configures the local Hugging Face loader for Gemma 4.
    This function interacts with Modal's environment variables to 
    authenticate and load the model into VRAM.
    """
    
    # 1. Pull Token from Modal Secret Manager
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found. Ensure the Modal Secret is attached.")

    # 2. Optimization: 4-bit Quantization
    # This allows a 12B model to run on ~8-10GB of VRAM with high speed.
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    print(f"--- [ADK SYSTEM] Loading {model_id} into GPU memory ---")

    # 3. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_id, 
        token=hf_token
    )

    # 4. Load Model
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=quant_config,
        device_map="auto", # Automatically balances across available Modal GPUs
        token=hf_token,
        trust_remote_code=True
    )

    return model, tokenizer

class GemmaInferenceEngine:
    """
    A simple wrapper used by the ADK Agent to run local inference 
    without needing a cloud API.
    """
    def __init__(self, model_id: str):
        self.model, self.tokenizer = get_gemma_model_config(model_id)

    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        outputs = self.model.generate(
            **inputs, 
            max_new_tokens=max_tokens,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Strip the prompt from the output to get only the agent's response
        return decoded[len(prompt):].strip()
