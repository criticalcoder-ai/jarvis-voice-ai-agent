from typing import List, Dict

from pydantic import BaseModel

class ModelConfig(BaseModel):
    model_id: str
    display_name: str
    available_on_guest: bool

MODELS: Dict[str, ModelConfig] = {
    "openai/gpt-4.1-mini": ModelConfig(
        model_id="openai/gpt-4.1-mini",
        display_name="GPT-4.1 Mini (OpenAI)",
        available_on_guest=False
    ),
    "openai/gpt-4o-mini": ModelConfig(
        model_id="openai/gpt-4o-mini",
        display_name="GPT-4o Mini (OpenAI)",
        available_on_guest=False
    ),
    "openai/gpt-4.1-nano": ModelConfig(
        model_id="openai/gpt-4.1-nano",
        display_name="GPT-4.1 Nano (OpenAI)",
        available_on_guest=True
    ),
    "google/gemini-2.5-flash": ModelConfig(
        model_id="google/gemini-2.5-flash",
        display_name="Gemini 2.5 Flash (Google)",
        available_on_guest=True
    ),
    "meta-llama/llama-4-maverick": ModelConfig(
        model_id="meta-llama/llama-4-maverick",
        display_name="LLaMA 4 Maverick (Meta)",
        available_on_guest=False
    ),
    "meta-llama/llama-4-scout": ModelConfig(
        model_id="meta-llama/llama-4-scout",
        display_name="LLaMA 4 Scout (Meta)",
        available_on_guest=True
    ),
}

def get_all_models() -> List[ModelConfig]:
    return list(MODELS.values())

def get_model_by_id(model_id: str) -> ModelConfig:
    return MODELS[model_id]
