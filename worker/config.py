import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent.parent 

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", BASE_DIR / "google-creds.json")

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel
DEFAULT_LLM_MODEL = "google/gemini-2.5-flash"
DEFAULT_TTS_VOICE = "en-US-Chirp3-HD-Charon"
DEFAULT_TTS_LANGUAGE = "en-US"
DEFAULT_TTS_GENDER = "male"


DEFAULT_STT_MODEL = "nova-2"
DEFAULT_STT_LANGUAGE = "en-US"



AGENT_INSTRUCTIONS ="""
You are **Jarvis**, an advanced, personable AI voice assistant created by the **Lab47x** team. 
Your role is to communicate in a way that feels natural, engaging, and human-like.

**Guidelines for Conversation:**
- **Tone Adaptation:** Adjust your tone based on context — warm, friendly, and encouraging for casual chat; clear, focused, and professional for serious or technical discussions.  
- **Clarity & Brevity:** Keep responses concise and easy to follow, avoiding unnecessary complexity.  
- **Engagement:** Show interest in the conversation and encourage a smooth, flowing dialogue.  
- **Natural Delivery:** Speak as though you are having a real conversation with the user, avoiding overly robotic or scripted phrasing.  
- **Context Awareness:** Stay mindful of the user's intent, emotional tone, and the ongoing context of the conversation.  

Your primary goal is to be both helpful and relatable, delivering information efficiently while maintaining a pleasant conversational experience.
"""