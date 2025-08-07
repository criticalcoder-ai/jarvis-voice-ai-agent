from typing import Dict, List
from pydantic import BaseModel


class VoiceConfig(BaseModel):
    voice_id: str
    display_name: str
    language: str
    type: str
    gender: str
    available_on_guest: bool


VOICES: Dict[str, VoiceConfig] = {
    # --- FEMALE VOICES ---
    "en-US-Wavenet-C": VoiceConfig(
        voice_id="en-US-Wavenet-C",
        display_name="US Female - Wavenet C",
        language="English (US)",
        type="wavenet",
        gender="female",
        available_on_guest=True
    ),
    "en-US-Neural2-G": VoiceConfig(
        voice_id="en-US-Neural2-G",
        display_name="US Female - Neural2 G",
        language="English (US)",
        type="neural2",
        gender="female",
        available_on_guest=False
    ),
    "en-GB-Wavenet-F": VoiceConfig(
        voice_id="en-GB-Wavenet-F",
        display_name="UK Female - Wavenet F",
        language="English (UK)",
        type="wavenet",
        gender="female",
        available_on_guest=True
    ),
    "en-IN-Chirp3-HD-Erinome": VoiceConfig(
        voice_id="en-IN-Chirp3-HD-Erinome",
        display_name="Indian Female - Chirp3 Erinome",
        language="English (India)",
        type="chirp3-hd",
        gender="female",
        available_on_guest=False
    ),

    # --- MALE VOICES ---
    "en-US-Wavenet-D": VoiceConfig(
        voice_id="en-US-Wavenet-D",
        display_name="US Male - Wavenet D",
        language="English (US)",
        type="wavenet",
        gender="male",
        available_on_guest=True
    ),
    "en-GB-Neural2-B": VoiceConfig(
        voice_id="en-GB-Neural2-B",
        display_name="UK Male - Neural2 B",
        language="English (UK)",
        type="neural2",
        gender="male",
        available_on_guest=False
    ),
    "en-IN-Chirp3-HD-Tarun": VoiceConfig(
        voice_id="en-IN-Chirp3-HD-Tarun",
        display_name="Indian Male - Chirp3 Tarun",
        language="English (India)",
        type="chirp3-hd",
        gender="male",
        available_on_guest=False
    ),
}


def get_voice_by_id(voice_id: str) -> VoiceConfig:
    return VOICES[voice_id]

def get_all_voices() -> List[VoiceConfig]:    
    return list(VOICES.values())