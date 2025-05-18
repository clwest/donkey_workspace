import os
import logging
from elevenlabs import ElevenLabs

logger = logging.getLogger("django")


def generate_elevenlabs_tts(
    prompt: str, voice_id: str, output_format: str = "mp3_44100_128"
) -> bytes:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("Missing ElevenLabs API key")

    client = ElevenLabs(api_key=api_key)

    try:
        audio = client.text_to_speech(
            text=prompt,
            voice_id=voice_id,
            model_id="eleven_monolingual_v1",
            voice_settings={"stability": 0.5, "similarity_boost": 0.5},
            output_format=output_format,
        )
        return audio
    except Exception as e:
        logger.exception("Failed to generate TTS")
        raise
