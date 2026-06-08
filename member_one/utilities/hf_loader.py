import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

#not using below because of OOM concerns
#hf_loader uses 4-bit quantization to squeeze 12B model down to about 8GB of VRAM
#allowing it to run lightning-fast with plenty of room for long book discussions.
#from transformers import AutoProcessor, AutoModelForImageTextToText
#processor = AutoProcessor.from_pretrained("google/gemma-4-12B")
#model = AutoModelForImageTextToText.from_pretrained("google/gemma-4-12B")

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
    
    # Ensure padding token is explicitly set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 4. Load Model
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=quant_config,
        device_map="auto", 
        token=hf_token,
        trust_remote_code=True
    )

    return model, tokenizer

class GemmaInferenceEngine:
    """
    An optimized wrapper used by the ADK Agent to run local inference 
    without needing a cloud API.
    """
    def __init__(self, model_id: str):
        self.model, self.tokenizer = get_gemma_model_config(model_id)

    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        # Explicitly generate the attention mask for stable multi-turn IRC logs
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=True).to("cuda")
        input_length = inputs.input_ids.shape[1]
        
        # Disable gradient calculation to save VRAM during active chat
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # FIX: Slice the tensor to decode ONLY the newly generated tokens
        new_tokens = outputs[0][input_length:]
        decoded = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        return decoded.strip()
