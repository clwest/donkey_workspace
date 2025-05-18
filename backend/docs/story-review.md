story/utils/image_captioning.py

    thinking for 21s

    thinking for 24s

    codex
    1. 📋 Purpose
           Provides a helper, `generate_alt_text_and_caption`, which uses OpenAI’s chat API to produce a concise image alt-text and a whimsical caption for a children’s storybook image,
    given a seed prompt and a snippet of story context.
        2. ✅ Good Practices


            * Type hint on the return type (`Tuple[str, str]`) makes it clear what to expect.

            * Clean separation of system vs. user messages to steer the model’s behavior.

            * Fallback parsing logic: if the LLM doesn’t emit two labeled lines, it still returns something rather than crashing.
        3. ⚠️ Concerns or Smells


            * Hard-coded model name (`"gpt-4.1"`) and no way to override it for A/B testing or fallback.

            * No error handling: network failures, missing API key, or unexpected API responses will throw unhandled exceptions.

            * Global instantiation of `client = OpenAI(api_key=…)` at import time makes it hard to inject a mock client in tests.

            * Parsing by splitting on lines and stripping labels (“Alt-text:”, “Caption:”) is brittle if the model varies its formatting (e.g. extra whitespace, different labels).

            * No logging of the request or response content, so failures or odd outputs are hard to debug.

            * No docstring on the function to explain parameters, expected format of the model output, or side effects.
        4. 🔧 Suggestions


            * Add a docstring explaining inputs/outputs, formatting expectations, and potential exceptions.

            * Inject the OpenAI client (e.g. pass it into the function or class) to allow mocking and configuration.

            * Parameterize the model name (via a default argument, settings, or environment variable) rather than hard-coding `"gpt-4.1"`.

            * Wrap the API call in a `try/except` block, log exceptions, and return a sensible default (e.g. `("", "")`) on failure.

            * Use `textwrap.dedent` on your prompt strings to avoid unintended leading whitespace in the LLM input.

            * Strengthen parsing by using a small regex to extract “Alt-text:” and “Caption:” fields, or require the model to return JSON for more robust downstream handling.

            * Add unit tests for: correct parsing when the response has two lines, fallback when it has one line or labels are missing, and error handling on API failure.
        5. 🔗 Cross-App Impacts


            * Consumers in the story module (e.g. `story.services` or view logic) depend on the tuple format of `(alt_text, caption)`. Changes to return types or parsing will break any
    code that unpacks or displays these values.

            * Relies on environment variable `OPENAI_API_KEY` and the OpenAI SDK; any upgrade or change in the SDK’s interface or auth mechanism needs corresponding updates here.
        6. 🧪 Testing Ideas


            * Mock `client.chat.completions.create` to return a fake payload with:
                 • Exactly two lines labeled with “Alt-text:” and “Caption:” → verify correct extraction.
                 • A single unlabelled line → verify fallback assigns it to `alt_text` and leaves `caption` empty.
                 • Unexpected formatting (e.g. JSON blob, extra blank lines) → ensure the parser doesn’t crash.

            * Simulate an exception from `client` (e.g. timeout) and assert that the function handles it gracefully (after adding error handling).

            * Integration test with a stubbed local OpenAI emulator (or a saved fixture) to verify end-to-end behavior against a known prompt/response.

    Review complete. Ready for next file.

story/utils/openai_story.py

    command.stdout (code: 0, duration: 0s)

    from openai import OpenAI
    import os
    from typing import Tuple, List, Dict, Optional

    ... (44 more lines)

    thinking for 12s

    thinking for 12s

    command

    $ wc -l story/utils/openai_story.py

    command.stdout (code: 0, duration: 0s)

          47 story/utils/openai_story.py


    thinking for 26s

    codex
    1. 📋 Purpose
           Wraps the OpenAI chat API to generate a short, whimsical, age-appropriate children’s fairy tale given a seed prompt, optional theme, tags, title, and project name.
        2. ✅ Good Practices


            * Clear separation of “system” instructions (defining the assistant’s persona and constraints) from the “user” content.

            * Uses Python type hints (`Optional[str]`, `List[str]`) on the function signature to document expected inputs.

            * Supports optional metadata (theme, tags, title, project_name) to steer the generated story.
        3. ⚠️ Concerns or Smells


            * Global instantiation of `client = OpenAI(api_key=os.getenv(...))` at import time makes testing difficult and couples the module to the environment.

            * Hard‐coded model name (`"gpt-4.1"`), `max_tokens=1000`, and `temperature=0.85` offer no easy way to override for experimentation or fallback.

            * The multi-line f-string for `user_prompt` is indented in code, injecting unintended leading whitespace into the prompt.

            * No error handling or logging around the API call—network errors or rate limits will raise uncaught exceptions.

            * Missing a docstring describing parameters, return value, and potential exceptions.
        4. 🔧 Suggestions


            * Add a comprehensive docstring to `generate_story` (describe inputs, side effects, output).

            * Inject the OpenAI client (e.g. pass `client` as an argument or use a factory) so tests can supply a mock, and the module need not read `os.getenv` at import.

            * Parameterize key settings (model, max_tokens, temperature) via function args or Django settings.

            * Normalize prompts with `textwrap.dedent()` to strip code indentation.

            * Wrap the API call in a `try/except`, log errors with `logger = logging.getLogger(__name__)`, and return a safe default or re-raise a controlled exception.

            * Consider returning structured data (e.g. dict with metadata) if you plan to track token usage or response details later.
        5. 🔗 Cross-App Impacts


            * Consumers in `story.services` or view modules rely on `generate_story` returning a plain string; changing its signature or return type will break them.

            * Tied to the `OPENAI_API_KEY` environment variable and the OpenAI SDK; any changes to authentication or SDK interface require updates here.
        6. 🧪 Testing Ideas


            * Mock `client.chat.completions.create` to return a dummy response object with a known `choices[0].message.content`, and assert the function returns it trimmed.

            * Test with only the required `prompt` parameter to ensure defaults (`Surprise me!`, default tags) appear correctly in `user_prompt`.

            * Test with all optional parameters provided, verifying they are interpolated into the prompt.

            * Simulate an API exception and confirm that, after adding error handling, the function logs appropriately and returns a graceful fallback.

            * Verify that leading whitespace from code indentation is removed when using `textwrap.dedent()`.

    Review complete. Ready for next file.

story/utils/prompt_helpers.py

    command.stdout (code: 0, duration: 0s)

    """
    Helper functions to manipulate prompts based on ThemeHelper presets.
    """
    from typing import Optional
    ... (14 more lines)

    thinking for 36s

    codex
    1. 📋 Purpose
           Provides small utilities to combine a user’s base prompt with a `ThemeHelper` preset’s positive or negative prompts when constructing image-generation inputs.
        2. ✅ Good Practices


            * Uses Python type hints (`-> str`, `-> Optional[str]`) and concise docstrings to document expected behavior.

            * Encapsulates prompt‐combination logic in one place, avoiding scatterings of `base + theme.prompt` throughout the codebase.

            * Handles the absence of a negative prompt cleanly by returning `None` when `theme.negative_prompt` is falsy.
        3. ⚠️ Concerns or Smells


            * The get-prompt logic simply injects `, {theme.prompt}` unconditionally, which can lead to double commas or awkward spacing if `base_prompt` already ends with punctuation.

            * No input validation or trimming: leading/trailing whitespace in either string will be preserved verbatim.

            * Very thin wrappers—almost one-liners—so it may not warrant its own module unless additional logic is expected.

            * Hard-coded delimiter (`, `) may not suit all prompt styles (some themes or engines might prefer newlines).
        4. 🔧 Suggestions


            * Enhance `get_prompt_for_theme` to normalize punctuation/spacing, for example:      combined = base_prompt.rstrip(' ,.')
                     return f"{combined}, {theme.prompt.strip()}"

            * Allow the delimiter to be configurable (e.g. via a parameter or constant) if some engines need newlines instead.

            * Add input validation and trimming: ensure `theme.prompt` is non-empty before combining.

            * Expand docstrings to mention side effects (e.g. that it always returns a comma-separated combination).

            * Write unit tests covering edge cases (empty base, base with trailing comma, empty theme.prompt).

            * If no further logic is anticipated, consider inlining these helpers back into the ThemeHelper serializer or view logic to reduce indirection.
        5. 🔗 Cross-App Impacts


            * Depends on `images.models.ThemeHelper`; renaming its `prompt` or `negative_prompt` fields will break these helpers.

            * Used by any image-generation orchestration code that applies theme presets—changing delimiter behavior will affect all themed prompts.
        6. 🧪 Testing Ideas


            * Test `get_prompt_for_theme` with:
                 • A normal base and theme prompt → expect `"base, theme"`.
                 • A base ending in comma or period → expect punctuation normalized (no double comma).
                 • Theme prompt containing leading/trailing whitespace → expect it stripped.

            * Test `get_negative_prompt_for_theme` when `theme.negative_prompt` is a non-empty string vs. an empty string or `None`.

            * Validate that combining extremely long base or theme prompts still returns a single string without errors.

    Review complete. Ready for next file

story/utils/story_generation.py

    thinking for 29s

    codex
    1. 📋 Purpose
           Orchestrates end‐to‐end story media creation by:


            * Generating a children’s story text via LLM

            * Producing image alt‐text and caption

            * Persisting a `Story` record

            * Creating an `Image` record and dispatching a Stable Diffusion task

            * Optionally enqueueing TTS narration

            * Linking everything to an optional `Project`
        2. ✅ Good Practices


            * Combines all related steps in one high-level function, making it easy to follow the workflow.

            * Delegates LLM calls to specialized utilities (`generate_story`, `generate_alt_text_and_caption`), keeping this module focused on orchestration.

            * Persists intermediate outputs (story text, alt‐text, caption) in the database, ensuring traceability and auditability.
        3. ⚠️ Concerns or Smells


            * Hard-coded status strings (`"completed"`, `"pending"`) and title‐truncation logic (`prompt[:100]`) may not reflect true domain invariants.

            * `theme` and `tags` are accepted as raw values (string, list) — unclear if they match the `Story.theme` and `Story.tags` field types (could be a foreign key or JSONField).

            * No error handling or logging around LLM calls or database writes; a failure in the middle could leave half-baked records.

            * The import `from django.utils import timezone` is unused.

            * Missing docstring, return type hint, and type annotations for most parameters (e.g., `image_style`, `narrator_voice`).

            * Synchronous LLM calls block request threads; consider backgrounding or making the whole workflow asynchronous.
        4. 🔧 Suggestions


            * Add a function‐level docstring and full type hints, including return type (`-> Story`).

            * Replace magic strings with model choice constants or enums for `status`.

            * Validate or coerce `theme` and `tags` to the correct types before saving (e.g., lookup a `ThemeHelper` instance, ensure tags is a list of strings).

            * Wrap each major step in try/except and log errors to avoid partial failures (e.g., using `logger = logging.getLogger(__name__)`).

            * Remove unused imports (`timezone`) and ensure only needed dependencies are imported.

            * Consider moving this orchestration into a Celery task chain so that LLM calls and image generation run off the web thread, improving responsiveness.
        5. 🔗 Cross-App Impacts


            * Relies on `story.utils.openai_story`, `story.utils.image_captioning`, Tasks in `images.tasks` and `tts.tasks`, plus models from `images`, `story`, `project`, and `tts` apps.
     Changes in any of these modules (API signatures, field names, task APIs) will break this workflow.
        6. 🧪 Testing Ideas


            * Unit‐test `create_full_story_with_media` by mocking `generate_story` and `generate_alt_text_and_caption` to return known outputs; verify that a `Story` and `Image` are
    created with the expected fields.

            * Test that `process_sd_image_request.delay` and `queue_tts_story.delay` are called when appropriate (use `celery_app` testing fixtures or monkeypatch).

            * Validate behavior when `narrator_voice` is `None` (no TTS task) vs. provided.

            * Simulate LLM or DB exceptions (patch utilities to throw) and assert that errors are caught/logged (after adding error handling).

            * Integration test across apps: call the real function in a test database and ensure tasks are enqueued and models linked correctly.

    Review complete. Ready for next file.

story/tasks.py

    command.stdout (code: 0, duration: 0s)

    from celery import shared_task
    from story.models import Story
    from story.utils.openai_story import generate_story
    from django.utils.timezone import now
    ... (159 more lines)

    thinking for 11s

    command

    $ sed -n '200,350p' story/tasks.py

    command.stdout (code: 0, duration: 0s)


    thinking for 104s

    codex
    1. 📋 Purpose
           Defines two Celery background tasks for the Story app:


            * `generate_story_task(story_id)`: Orchestrates end-to-end story generation—enriching the prompt (theme, character), calling the LLM, auto-filling the title, persisting
    `Story`, splitting into paragraphs, creating and queuing `Image` tasks, and generating alt-text & caption.

            * `embed_story_chunks(story_id)`: Breaks the story into paragraph chunks, generates embeddings, computes similarity against `TagConcept`s, and upserts `StoryChunkEmbedding`
    records with inferred tags.
        2. ✅ Good Practices


            * Uses `@shared_task` to keep heavy I/O off the request thread and improve scalability.

            * Comprehensive logging at `info`, `debug`, `warning`, and `error` levels to trace progress and failures.

            * Fine-grained error handling: theme and character enrichment errors fall back gracefully; per-chunk embedding exceptions are caught so one bad chunk doesn’t abort the entire
    process.

            * Separates generation and embedding into two tasks, enabling independent scaling and retries.
        3. ⚠️ Concerns or Smells


            * Logger is hard-coded to `"django"`; using `logger = logging.getLogger(__name__)` would provide more context.

            * Duplicate scheduling of `process_sd_image_request.delay(image.id)` for the last image—once inside the paragraph loop and once again after saving `story.image`.

            * Hard-coded magic strings and numbers: `model="gpt-4.1"`, image dimensions, step counts, LLM prompt snippets, status strings (`"queued"`, `"completed"`).

            * In-task imports (re-importing `Story`, `ImageModel`, `now`) are unnecessary and add cognitive overhead.

            * Unused import: `Image as ImageModel` is imported in `generate_story_task` but never used.

            * No function docstrings or type hints on the task definitions, making it harder to discover expected arguments and side effects.

            * Character enrichment silently swallows all exceptions—even ones you might want to know about.
        4. 🔧 Suggestions


            * Switch to a module-level logger:      logger = logging.getLogger(__name__)

            * Remove the extra `process_sd_image_request.delay(image.id)` after the loop to avoid double-queuing the same image.

            * Extract hard-coded settings (models, image size, steps, prompt templates, status values) into module constants or Django settings, so they can be tuned without code changes.


            * Clean up imports: move all imports to the top of the module and remove unused ones (e.g. `ImageModel`).

            * Add docstrings and type hints to `generate_story_task` and `embed_story_chunks`, documenting input parameters and return behavior.

            * Consider breaking the image-generation loop into a helper function for readability and testing.

            * Tighten exception handling: catch only expected exceptions (e.g. `ThemeHelper.DoesNotExist`, `OpenAIError`) and let truly unexpected errors bubble to the outer Celery error
    handler.
        5. 🔗 Cross-App Impacts


            * Calls `generate_story` in `story.utils.openai_story` and `generate_alt_text_and_caption` in `story.utils.image_captioning`; changes there (signature or return value) will
    break these tasks.

            * Depends on `Story`, `StoryChunkEmbedding`, and `TagConcept` models in the `story` and `embeddings` apps; schema or API changes there will have to be mirrored here.

            * Queues tasks in `images.tasks` (`process_sd_image_request`) and `tts.tasks`; changes in those tasks’ signatures or names will break the orchestration.
        6. 🧪 Testing Ideas


            * Unit-test `generate_story_task` by mocking:
                 • `Story.objects.get` to return a fake story instance with/without theme and character.
                 • `generate_story` and `generate_alt_text_and_caption` to return controlled outputs.
                 • `Image.objects.create` and `process_sd_image_request.delay` to capture calls.
                 Verify that the story’s fields are updated correctly and exactly one image task per paragraph is scheduled.

            * Test edge cases: missing `story_id`, no `generated_text`, story with no paragraphs.

            * Unit-test `embed_story_chunks` by mocking:
                 • A story record with generated text divided into known chunks.
                 • `generate_embedding` to return deterministic vectors.
                 • `compute_similarity` to assign clear tag matches above/below threshold.
                 Verify that `StoryChunkEmbedding` is created or updated, and that the correct tags are set.

            * Integration test running both tasks in sequence on a test database to ensure end-to-end coverage.

    Review complete. Ready for next file.

story/views.py

    command.stdout (code: 0, duration: 0s)

            )

    class StoryCreateView(APIView):
        permission_classes = [IsAuthenticated]
    ... (29 more lines)

    thinking for 26s

    command

    $ sed -n '1,200p' story/models.py

    command.stdout (code: 0, duration: 0s)

    from django.db import models
    from django.contrib.auth import get_user_model
    from django.conf import settings
    from django.contrib.postgres.fields import ArrayField
    ... (74 more lines)

    thinking for 47s

    codex
    1. 📋 Purpose
           Exposes REST endpoints for managing `Story` objects and related workflows in the Story app:


            * CRUD operations and list/detail via `StoryViewSet` (including queuing LLM generation, retry, audio TTS, and paragraph‐level tagging)

            * Nested project‐scoped story management via `ProjectStoriesViewSet`

            * High‐level “create with media” endpoint via `StoryCreateView` that orchestrates story, image, and audio creation
        2. ✅ Good Practices


            * Leverages DRF `ModelViewSet` and `@action` decorators to minimize boilerplate and provide rich, RESTful URL patterns.

            * Applies appropriate permission classes (`IsAuthenticatedOrReadOnly` for read/write safety, `IsAuthenticated` for TTS/tagging actions).

            * Decouples heavy I/O into Celery tasks (`generate_story_task`, `embed_story_chunks`, `queue_tts_story`, `process_sd_image_request`), keeping the API layer responsive.
        3. ⚠️ Concerns or Smells


            * Duplicate logic/unused methods:
                 • `perform_create` schedules the story‐generation task, but `create()` override also schedules it—`perform_create` is never invoked.
                 • `status` is imported twice.

            * Mixed patterns: two story‐creation endpoints (`ModelViewSet.create` vs `StoryCreateView.post`), risking inconsistency.

            * Bare `except Exception:` blocks around character enrichment and in task imports swallow unexpected errors without logging.

            * Hardcoded magic strings and parameters:
                 • Task queue payloads (`prompt_text`, `voice_style`, `provider`) assume specific Celery task signatures.
                 • Default TTS provider index (`StoryAudio.TTS_PROVIDERS[0][0]`).

            * No pagination on list endpoints—potential performance bottleneck for large story sets.

            * Minimal or missing docstrings and type hints on view methods and custom actions.

            * Inconsistent error responses: some return 400, others 404, but message formats vary.
        4. 🔧 Suggestions


            * Consolidate story creation into one pattern: either rely on `ModelViewSet.create()` + `perform_create()` or use the custom `APIView`. Remove duplication.

            * Use a module‐level logger (`logger = logging.getLogger(__name__)`) and replace bare `except:` with targeted exception handling + `logger.error()/warning()`.

            * Extract magic strings, default pagination size, and Celery task argument names into constants or Django settings, ensuring consistency and easier tuning.

            * Add docstrings and type annotations to every custom action and view to clarify expected inputs and outputs.

            * Introduce pagination classes on `StoryViewSet` and `ProjectStoriesViewSet` to guard against large result sets.

            * Validate and sanitize incoming parameters (e.g. `voice_style`, `provider`) against allowed choices before scheduling tasks.

            * Standardize error response format (e.g. always `{ "detail": "..."} `) for easier client handling.
        5. 🔗 Cross-App Impacts


            * Depends on `story.tasks` (`generate_story_task`, `embed_story_chunks`) and `story.utils.story_generation.create_full_story_with_media` for backend workflows; any signature
    or behavior change there breaks views.

            * Interacts with `images.models.Image` and `images.tasks.process_sd_image_request`—changes to image‐generation task API affect `generate_audio` and creation logic.

            * Relies on `tts.models.StoryAudio` and `tts.tasks.queue_tts_story`—their model/field or task signature changes cascade here.

            * Uses `embeddings.models.StoryChunkEmbedding` in `chunk_tags` and `tags` actions; schema changes in embeddings will ripple.
        6. 🧪 Testing Ideas


            * Unit‐test `StoryViewSet.create`: mock the serializer, verify that `generate_story_task.delay` is called once and the response contains the serialized story data.

            * Test `retry_generation` for scenarios: non‐existent ID → 404; already generated story → 400; queued story → 202 and task enqueued.

            * Test `generate_audio`: missing story → 404; no text → 400; valid case → `StoryAudio` created, `queue_tts_story.delay` called, correct serializer output.

            * Test `tag_chunks`: valid story → `embed_story_chunks.delay` called; invalid → 404.

            * Test `chunk_tags` and `tags` aggregation: with a seeded `StoryChunkEmbedding` queryset, verify correct JSON shape and top‐5 selection.

            * Integration test for `ProjectStoriesViewSet`: verify scoping by `project_pk` and `user`, correct creation with `perform_create`.

            * Test `StoryCreateView`: provide valid payloads (with/without optional fields), assert full orchestration kicks off (calls `create_full_story_with_media`) and returns
    expected JSON.

    Review complete. Ready for next file.
