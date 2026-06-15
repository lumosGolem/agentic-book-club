## offloading model weights to Modal.com

# club_members/member_one/utils/hf_loader.py

import requests


MODAL_URL = "https://erdincselin--bookstore-generate-dev.modal.run"


class GemmaInferenceEngine:

    def __init__(self, model_name: str = "google/gemma-4-12B-it"):
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        max_tokens: int = 150,
    ) -> str:

        response = requests.post(
            MODAL_URL,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": max_tokens,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]