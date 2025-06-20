 # Story App Model Overview

 This document walks through the Django models in `story/models.py`, outlines their fields, relations, and suggests improvements.

 ---

 ## 1. Story

 **Purpose**: Represents a generated or user-authored narrative, with optional media attachments and metadata for publishing and gamification.

 **Fields**:
 - `status` (CharField, choices): Lifecycle state (`queued`, `generating`, `completed`, `failed`).
 - `user` (ForeignKey → User): Owner or author of the story.
 - `title` (CharField[200], blank): Optional title; blank until set.
 - `prompt` (TextField): Seed prompt or instruction for generation.
 - `summary` (TextField, blank/null): Short summary or blurb.
 - `generated_text` (TextField): Full narrative content.
 - `created_at` (DateTimeField): Creation timestamp.
 - `updated_at` (DateTimeField): Last modification timestamp.
 - `published_at` (DateTimeField, null/blank): Timestamp when story was published.

 **Media & Attachments**:
 - `image` (ForeignKey → images.Image, null/blank): Linked illustration.
 - `cover_image_url` (URLField, blank/null): URL for a cover image.
 - `tts` (OneToOneField → tts.StoryAudio, null/blank): Associated TTS audio output.

 **Organization & Metadata**:
 - `project` (ForeignKey → project.Project, null/blank): Parent project for grouping.
 - `theme` (CharField[100], blank/null): Free-text theme label.
 - `tags` (ArrayField of CharField[50]): List of user-defined tags.
 - `is_reward` (BooleanField): Flag for gamification rewards.
 - `reward_reason` (CharField[255], blank/null): Rationale for reward allocation.

 **Illustration Styling & Characters**:
 - `style` (ForeignKey → images.PromptHelper, null/blank): Prompt template for story visuals.
 - `character` (ForeignKey → characters.CharacterProfile, null/blank): Legacy single-character link.
 - `characters` (ManyToManyField → characters.CharacterProfile, blank): Multiple associated characters.
 - `image_caption` (TextField, blank/null): Caption for the linked image.
 - `image_alt_text` (CharField[300], blank/null): Accessibility text for images.

 **Meta**:
 - `indexes`: Composite indexes on `created_at` and `user` for efficient querying.

 **Methods & Str**:
 - `__str__()`: Returns `title` or fallback string including `id` and `user`.

 **Notes & Improvements**:
 - Replace free-text `theme` with FK to a `ThemeHelper` or dedicated `Theme` model.
 - Migrate `tags` from `ArrayField` to a ManyToMany `Tag` model for richer metadata and querying.
 - Add `ordering` in `Meta` (e.g., newest first) or default manager method.
 - Introduce slug or unique URL path for user-friendly story URLs.
 - Track `status` transitions via a separate history model or JSONField for audit.
 - Add `published` boolean alongside `published_at` for clarity.
 - Ensure cascade or on-delete behavior for linked media (images, TTS) aligns with UX expectations.
 - Remove the legacy `character` FK if superseded by `characters` M2M.
 - Add `created_by`/`updated_by` fields for audit when multiple authors are supported.
 - Index `status`, `project`, and `published_at` for filtering in listing endpoints.
 - Consider storing `prompt` metadata (e.g., tokens, language) in additional fields for analytics.

 ---

 # Cross-Model Connections & Gaps

 - **Media**: Integrates with `images.Image` and `tts.StoryAudio` for multi-modal content.
 - **Project**: References `project.Project` for story grouping but uses free-text `theme`.
 - **Characters**: Links to `characters.CharacterProfile` both in legacy single-FK and new M2M.
 - **PromptHelper**: Uses `images.PromptHelper` to stylize story visuals; potential naming misalignment.
 - **Tagging**: Ad-hoc `ArrayField` tagging; other apps use dedicated `Tag` models.

 # Summary of Recommended Improvements

 1. Standardize theme and tag relationships using FK/M2M to dedicated models.
 2. Implement friendly slugs and URL routing for stories.
 3. Enhance publication workflow with status history and explicit `published` flag.
 4. Consolidate character linking by removing deprecated `character` field.
 5. Add audit fields for multi-author support and versioning.
 6. Index and optimize filters on `status`, `user`, `project`, and `published_at`.
 7. Align naming of visual styles (e.g., introduce `StoryStyle` model rather than reusing `PromptHelper`).