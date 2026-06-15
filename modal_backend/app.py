import modal
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

app = modal.App("bookstore")

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
)

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


@app.function(
    gpu="A10G",
    image=image,
    scaledown_window=300,
)

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