"""
This module will:
        •	create the story,
        •	generate alt-text & caption,
        •	create the image (by calling your image generation task),
        •	optionally associate with a Project,
        •	and return the fully linked Story object."""

from story.utils.openai_story import generate_story
from story.utils.image_captioning import generate_alt_text_and_caption
from images.models import Image
from story.models import Story
from project.models import Project
from tts.models import StoryAudio
from images.tasks import process_sd_image_request
from tts.tasks import queue_tts_story

from django.utils import timezone


def create_full_story_with_media(
    user,
    prompt: str,
    theme: str = None,
    tags: list = None,
    image_style=None,
    narrator_voice=None,
    project: Project = None,
    is_reward: bool = False,
    reward_reason: str = None,
):
    # Step 1: Generate the story text
    story_text = generate_story(prompt, theme, tags)
    story_snippet = story_text[:300]

    # Step 2: Generate alt text + caption
    alt_text, caption = generate_alt_text_and_caption(prompt, story_snippet)

    # Step 3: Save the story object
    story = Story.objects.create(
        user=user,
        title=prompt[:100],  # you can overwrite this later with a custom title
        prompt=prompt,
        generated_text=story_text,
        status="completed",  # optionally set to queued then background it
        theme=theme or "",
        tags=tags or [],
        project=project,
        is_reward=is_reward,
        reward_reason=reward_reason,
    )

    # Step 4: Create the image object and dispatch async task
    image = Image.objects.create(
        user=user,
        prompt=prompt,
        description=caption,
        style=image_style,
        story=story,
        project=project,
        generation_type="initial",
        applied_prompt_suffix=alt_text,
        status="pending",
    )
    story.image = image
    story.save()

    process_sd_image_request.delay(image.id)

    # Step 5: Kick off optional TTS generation
    if narrator_voice:
        queue_tts_story.delay(story.id, narrator_voice)

    return story
