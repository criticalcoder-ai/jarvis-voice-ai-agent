from typing import Dict, List, Optional
from pydantic import BaseModel


class VoiceConfig(BaseModel):
    voice_id: str
    display_name: str
    language: str
    type: str
    gender: Optional[str] = None
    available_on_guest: bool


VOICES: Dict[str, VoiceConfig] = {
    "en-US-Chirp3-HD-Charon": VoiceConfig(
        voice_id="en-US-Chirp3-HD-Charon",
        display_name="US Male – Charon",
        language="en-US",
        type="chirp3-hd",
        gender="male",
        available_on_guest = True
    ),
    "en-US-Chirp3-HD-Kore": VoiceConfig(
        voice_id="en-US-Chirp3-HD-Kore",
        display_name="US Female – Kore",
        language="en-US",
        type="chirp3-hd",
        gender="female",
        available_on_guest = True
    ),
    "en-US-Chirp3-HD-Leda": VoiceConfig(
        voice_id="en-US-Chirp3-HD-Leda",
        display_name="US Female – Leda",
        language="en-US",
        type="chirp3-hd",
        gender="female",
        available_on_guest = False
    ),

    "en-GB-Chirp3-HD-Schedar": VoiceConfig(
        voice_id="en-GB-Chirp3-HD-Schedar",
        display_name="UK Male – Schedar",
        language="en-GB",
        type="chirp3-hd",
        gender="male",
        available_on_guest = True
    ),
    "en-GB-Chirp3-HD-Sulafat": VoiceConfig(
        voice_id="en-GB-Chirp3-HD-Sulafat",
        display_name="UK Female – Sulafat",
        language="en-GB",
        type="chirp3-hd",
        gender="female",
        available_on_guest = False
    ),
    "en-GB-Chirp3-HD-Zubenelgenubi": VoiceConfig(
        voice_id="en-GB-Chirp3-HD-Zubenelgenubi",
        display_name="UK Male – Zubenelgenubi",
        language="en-GB",
        type="chirp3-hd",
        gender="male",
        available_on_guest = False
    ),

    "en-US-Chirp3-HD-Aoede": VoiceConfig(
        voice_id="en-US-Chirp3-HD-Aoede",
        display_name="US Female – Aoede",
        language="en-US",
        type="chirp3-hd",
        gender="female",
        available_on_guest = False
    ),
}


def get_voice_by_id(voice_id: str) -> VoiceConfig:
    return VOICES[voice_id]


def get_all_voices() -> List[VoiceConfig]:
    return list(VOICES.values())
