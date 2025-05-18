# tts/tasks.py
import os
import base64
import logging
from django.utils.timezone import now
from celery import shared_task
from tts.models import StoryAudio
from tts.utils.openai_tts import generate_openai_tts
from tts.utils.elevenlabs_tts import generate_elevenlabs_tts
from django.core.files.base import ContentFile

logger = logging.getLogger("django")


@shared_task
def queue_tts_story(
    prompt_text: str, user_id: int = None, voice: str = "echo", provider: str = "openai"
):
    if not prompt_text:
        logger.warning("TTS prompt is empty, skipping.")
        return

    try:
        logger.info(
            f"🔊 TTS generation started | Provider: {provider} | Voice: {voice}"
        )

        # Create DB entry first to track status
        story = StoryAudio.objects.create(
            user_id=user_id,
            prompt=prompt_text,
            voice_style=voice,
            provider=provider,
            status="processing",
        )

        if provider == "openai":
            audio_bytes = generate_openai_tts(prompt_text, voice)
        elif provider == "elevenlabs":
            audio_bytes = generate_elevenlabs_tts(prompt_text, voice)
        else:
            raise ValueError(f"Unsupported TTS provider: {provider}")

        # Save as file
        filename = f"tts_{story.id}_{provider}.mp3"
        story.audio_file.save(filename, ContentFile(audio_bytes))

        # Also save base64 for fast access (optional)
        story.base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        story.status = "completed"
        story.completed_at = now()
        story.save()

        logger.info(f"✅ TTS generated & saved | Story ID: {story.id}")

    except Exception as e:
        logger.exception("🔥 TTS generation failed")
        if "story" in locals():
            story.status = "failed"
            story.save()


@shared_task
def queue_tts_scene(scene_audio_id: int):
    """Async task to generate TTS audio for a scene image."""
    from tts.models import SceneAudio
    from tts.utils.openai_tts import generate_openai_tts
    from tts.utils.elevenlabs_tts import generate_elevenlabs_tts
    from django.utils.timezone import now
    from django.core.files.base import ContentFile
    import base64
    import logging

    logger = logging.getLogger("django")
    try:
        scene = SceneAudio.objects.get(id=scene_audio_id)
        scene.status = "processing"
        scene.save()
        # Generate audio bytes
        if scene.provider == "openai":
            audio_bytes = generate_openai_tts(scene.prompt, scene.voice_style)
        elif scene.provider == "elevenlabs":
            audio_bytes = generate_elevenlabs_tts(scene.prompt, scene.voice_style)
        else:
            raise ValueError(f"Unsupported TTS provider: {scene.provider}")
        # Save audio file
        filename = f"scene_tts_{scene.id}_{scene.provider}.mp3"
        scene.audio_file.save(filename, ContentFile(audio_bytes))
        # Save base64 and mark completed
        scene.base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        scene.status = "completed"
        scene.completed_at = now()
        scene.save()
    except Exception:
        logger.exception("🔥 TTS scene generation failed")
        try:
            scene.status = "failed"
            scene.save()
        except:
            pass
