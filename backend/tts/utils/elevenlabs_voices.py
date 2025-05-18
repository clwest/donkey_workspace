import os
from elevenlabs import ElevenLabs


def get_elevenlabs_voices():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("Missing ElevenLabs API key")

    client = ElevenLabs(api_key=api_key)
    voices = client.get_voices()
    return voices
