import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

def get_qwen_model_config(model_id: str = "Qwen/Qwen3-14B"):
    """
    Configures the Hugging Face loader for Qwen3-14B.
    Optimized for non-thinking mode to maximize speed in IRC workflows.
    """
    hf_token = os.environ.get("HF_TOKEN")
    
    # Optimization: 4-bit Quantization (Essential for 14B on 24GB VRAM)
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 
    )

    print(f"--- [ADK SYSTEM] Loading {model_id} (Qwen Architecture) ---")

    tokenizer = AutoTokenizer.from_pretrained(
        model_id, 
        token=hf_token,
        trust_remote_code=True
    )
    
    # Ensure correct padding mapping for open text generation
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=quant_config,
        device_map="auto", 
        token=hf_token,
        trust_remote_code=True,
        attn_implementation="flash_attention_2" if torch.cuda.get_device_capability()[0] >= 8 else "eager"
    )

    return model, tokenizer

class QwenInferenceEngine:
    """
    Inference wrapper for Qwen3-14B within the ADK 2.0 Agent logic.
    """
    def __init__(self, model_id: str = "Qwen/Qwen3-14B"):
        self.model, self.tokenizer = get_qwen_model_config(model_id)

    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        # Generate clean attention inputs
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=True).to("cuda")
        input_length = inputs.input_ids.shape[1]
        
        # Free memory tracking and enforce non-thinking configurations
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                # Enforces direct response generation, completely bypassing the hidden <think> delay
                extra_generation_params={"enable_thinking": False} if hasattr(self.model, "generation_config") else {}
            )
        
        # FIX: Slice tokens by position first, avoiding string truncation bugs
        new_tokens = outputs[0][input_length:]
        decoded = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        return decoded.strip()
