 # TTS App Model Overview

 This document walks through each Django model in `tts/models.py`, outlines their purposes, fields, relations, and suggests improvements.

 ---

 ## 1. StoryAudio

 **Purpose**: Manages text-to-speech (TTS) generation for stories, producing audio files and previews linked to users and projects.

 **Fields**:
 - `user` (ForeignKey → User): Requesting user (nullable for system or guest).
 - `prompt` (TextField): Input text to be converted to speech.
 - `base64_audio` (TextField, blank/null): Base64-encoded audio for quick previews.
 - `audio_file` (FileField, blank/null): Stored audio file reference.
 - `project` (ForeignKey → project.Project, null/blank): Optional project context.
 - `story` (OneToOneField → story.Story, null/blank): Linked story for one-to-one mapping.
 - `voice_style` (CharField[100], blank/null): Identifier for voice style (e.g., echo, nova, or external ID).
 - `provider` (CharField[20], choices): TTS service provider (`openai`, `elevenlabs`).
 - `status` (CharField[20], choices): Processing state (`queued`, `processing`, `completed`, `failed`).
 - `model_backend` (CharField[50], choices): Backend selection for generation.
 - `theme` (CharField[100], blank/null): Free-text theme descriptor.
 - `tags` (ArrayField of CharField[50], default=list): List of user-defined tags.
 - `created_at`, `updated_at` (DateTimeField): Timestamps for creation and modification.

 **Meta**:
 - Indexes on `created_at` and `user` for efficient querying.

 **Notes & Improvements**:
 - Add `duration` (FloatField) to capture audio length.
 - Store `error_message` for failures and retry counts/status.
 - Normalize `theme` and `tags` into dedicated models for rich metadata and filtering.
 - Enforce cascade behavior on `story` deletion or use `SET_NULL` appropriately.
 - Add `created_by`/`updated_by` for audit when multiple agents can generate audio.
 - Consider storing audio metadata (bitrate, sample rate, format) in JSONField.

 ---

 ## 2. SceneAudio

 **Purpose**: Tracks TTS narration for individual scene images, enabling audio descriptions or storytelling tied to visual content.

 **Fields**:
 - `user` (ForeignKey → User): Requesting user (nullable).
 - `image` (ForeignKey → images.Image): Associated scene image.
 - `prompt` (TextField): Text prompt for scene narration.
 - `base64_audio` (TextField, blank/null): Base64 preview.
 - `audio_file` (FileField, blank/null): Stored file reference.
 - `voice_style` (CharField[100], blank/null): Voice identifier.
 - `provider` (CharField[20], choices): TTS service provider.
 - `status` (CharField[20], choices): Job status.
 - `task_id` (CharField[100], blank/null): External task identifier for tracking.
 - `created_at`, `updated_at`, `completed_at` (DateTimeField): Timestamps for lifecycle events.

 **Meta**:
 - Indexes on `created_at` and `image` for efficient retrieval.

 **Notes & Improvements**:
 - Add `duration` and `error_message` fields similar to `StoryAudio`.
 - Normalize tags or link to scene metadata for context-aware narration.
 - Consider merging common TTS behavior into an abstract base model or mixin.
 - Add `priority` or `scheduled_at` for queued narration tasks.

 ---

 # Cross-Model Connections & Gaps

 - **Story Integration**: `StoryAudio.story` ties directly into the `story` app; ensure consistent on-delete semantics.
 - **Image Narration**: `SceneAudio.image` connects to `images.Image`, enabling multimodal storytelling.
 - **Backend Consistency**: Both models share provider and status choices; abstracting into a shared mixin could reduce duplication.
 - **Tagging & Theming**: Free-text `theme` and array `tags` limit querying; consider dedicated `ThemeHelper` or `Tag` models.

 # Summary of Recommended Improvements

 1. Introduce an abstract `BaseTTS` model or mixin to encapsulate shared fields (`prompt`, `provider`, `status`, etc.).
 2. Normalize tags and themes into FK/M2M relationships for better filtering and management.
 3. Add audio metadata fields (`duration`, `format`, `bitrate`) and error logging.
 4. Enhance audit fields (`created_by`, `processed_by`) and include retry/backoff parameters.
 5. Implement cleanup of stale or failed audio jobs and limit storage growth.
 6. Index on `status`, `provider`, and `task_id` for operational monitoring (dashboards, alerts).