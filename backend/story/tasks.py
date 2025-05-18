from celery import shared_task
from story.models import Story
from story.utils.openai_story import generate_story
from django.utils.timezone import now
import logging
from images.models import Image
from images.tasks import process_sd_image_request
from story.utils.image_captioning import generate_alt_text_and_caption

logger = logging.getLogger("django")


@shared_task
def generate_story_task(story_id: int):
    from story.models import Story
    from django.utils.timezone import now
    from images.models import Image as ImageModel

    try:
        story = Story.objects.get(id=story_id)
        logger.info(f"📖 Generating story for ID {story_id}...")
        # Determine base prompt and enrich with theme if preset
        base_prompt = story.prompt or ""
        enriched_prompt = base_prompt
        # If a preset theme was selected, enrich prompt
        if getattr(story, "theme_id", None):
            try:
                from story.utils.prompt_helpers import get_prompt_for_theme
                from images.models import ThemeHelper

                theme_obj = ThemeHelper.objects.get(id=story.theme_id)
                enriched_prompt = get_prompt_for_theme(theme_obj, base_prompt)
                logger.debug(
                    f"🔧 Enriched prompt with theme '{theme_obj.name}': {enriched_prompt}"
                )
            except Exception:
                # Fallback to base prompt on any error
                enriched_prompt = base_prompt
        # If a character is linked, enrich prompt with character context
        if getattr(story, "character", None):
            try:
                char = story.character
                enriched_prompt = f"{enriched_prompt}\n\nCharacter: {char.name}\nBackstory: {char.backstory}"
                logger.debug(
                    f"🧝 Enriched prompt with character '{char.name}': {enriched_prompt}"
                )
            except Exception:
                # Continue with existing enriched_prompt on error
                pass
        # 🔮 Generate the story text using enriched prompt
        output = generate_story(
            prompt=enriched_prompt,
            theme=story.theme,
            tags=story.tags,
            title=story.title,
            project_name=story.project.title if story.project else None,
        )

        # 📝 Auto-fill title if missing
        if not story.title:
            first_line = output.strip().split("\n")[0]
            story.title = first_line.replace("**", "").strip()[:200]

        story.generated_text = output
        story.status = "completed"
        story.updated_at = now()
        story.save(update_fields=["generated_text", "status", "updated_at", "title"])
        logger.info(f"✅ Story {story_id} generation complete!")
        paragraphs = [
            p.strip() for p in story.generated_text.split("\n\n") if p.strip()
        ]

        # 🎨 Auto-generate an image linked to the story + project
        for idx, paragraph in enumerate(paragraphs):
            image = Image.objects.create(
                user=story.user,
                prompt=paragraph,
                story=story,
                order=idx,
                description=f"Illustration for paragraph {idx+1}",
                alt_text=f"Paragraph {idx+1} — {paragraph[:50]}",
                width=1024,
                height=768,
                style=story.style,
                steps=50,
                engine_used="stable-diffusion",
                status="queued",
            )
            process_sd_image_request.delay(image.id)

        # 🧠 Generate alt-text + caption based on story context
        try:
            alt_text, caption = generate_alt_text_and_caption(
                prompt=story.prompt,
                story_snippet=story.generated_text[:400],  # Keep context short
            )
            story.image_alt_text = alt_text
            story.image_caption = caption
            logger.info(f"📝 Generated alt-text and caption for Story {story_id}")
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to generate alt-text/caption for Story {story_id}: {e}"
            )

        story.image = image
        story.save(update_fields=["image"])
        process_sd_image_request.delay(image.id)
        logger.info(
            f"🖼️ Image generation queued for Story {story_id} (Image {image.id})"
        )

    except Story.DoesNotExist:
        logger.warning(f"❌ Story ID {story_id} not found.")
    except Exception as e:
        logger.exception(f"🔥 Failed to generate story {story_id}: {e}")


@shared_task
def embed_story_chunks(story_id: int):
    """
    Generate embeddings for each paragraph of a story and infer semantic tags.
    """
    import logging
    from story.models import Story
    from embeddings.helpers.helpers_processing import generate_embedding
    from embeddings.vector_utils import compute_similarity
    from embeddings.models import TagConcept, StoryChunkEmbedding

    logger = logging.getLogger("django")
    try:
        story = Story.objects.get(id=story_id)
    except Story.DoesNotExist:
        logger.warning(f"🛑 Story {story_id} not found for chunk embedding.")
        return

    text = story.generated_text or story.prompt or ""
    if not text:
        logger.warning(f"⚠️ No text to embed for Story {story_id}.")
        return

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    tag_concepts = list(TagConcept.objects.all())

    for idx, para in enumerate(paragraphs):
        try:
            embedding = generate_embedding(para)
            if not embedding:
                logger.warning(
                    f"⚠️ Empty embedding for chunk {idx} of Story {story_id}."
                )
                continue

            scores = []
            for tc in tag_concepts:
                vec_tc = list(tc.embedding)
                sim = compute_similarity(embedding, vec_tc)
                scores.append((sim, tc))

            threshold = 0.75
            matched = [tc for sim, tc in scores if sim >= threshold]
            if not matched and scores:
                top3 = sorted(scores, key=lambda x: x[0], reverse=True)[:3]
                matched = [tc for _, tc in top3]

            chunk, created = StoryChunkEmbedding.objects.update_or_create(
                story=story,
                paragraph_index=idx,
                defaults={
                    "text": para,
                    "embedding": embedding,
                },
            )
            chunk.tags.set(matched)
            chunk.save()
            tag_names = [tc.name for tc in matched]
            logger.info(
                f"✅ Chunk {idx} of Story {story_id} embedded with tags: {tag_names}"
            )
        except Exception as e:
            logger.error(
                f"🔥 Error embedding chunk {idx} for Story {story_id}: {e}",
                exc_info=True,
            )
