# tts/utils/openai_tts.py
from openai import OpenAI
import logging

client = OpenAI()
logger = logging.getLogger("django")


def generate_openai_tts(prompt: str, voice: str = "echo", model: str = "tts-1"):
    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=prompt,
        )
        return response.read()
    except Exception as e:
        logger.error(f"OpenAI TTS error: {e}")
        raise
