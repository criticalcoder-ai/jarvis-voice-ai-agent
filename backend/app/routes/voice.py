from typing import List
from fastapi import APIRouter
from app.model_config import ModelConfig, get_all_models
from app.voice_config import get_all_voices, VoiceConfig



router = APIRouter(tags=["voice"])

@router.get("/voices", response_model=List[VoiceConfig], status_code=200)
def list_voices():
    return get_all_voices()



@router.get("/models", response_model=List[ModelConfig], status_code=200)
def list_models():
    return get_all_models()
