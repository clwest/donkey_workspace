# Characters App Model Overview

This document walks through each Django model in `characters/models.py`, shows how they relate, and points out gaps or improvement ideas.

---

## 1. CharacterProfile

**Purpose**: Defines a character entity for chat or visual usage.
**Fields**:

- `name` (unique)
- `slug` (unique, auto-generated)
- `description`, `backstory`
- `personality_traits` (JSON list)
- `is_public`, `is_featured`
- `created_by` (User FK)
- `created_at`
- `project` (Project FK)
- M2M `character_styles` (PromptHelper)

**Relations**:

- One-to-many → `CharacterStyle` (`styles`)
- One-to-many → `CharacterReferenceImage` (`reference_images`)
- One-to-one → `CharacterTrainingProfile` (`training_profile`)
- Many-to-many → `CharacterTag` (`tags`)
- Many-to-many → `images.PromptHelper` (`character_styles`)

**Notes & Improvements**:

- Enforce slug uniqueness on updates and migrations.
- Validate that public characters have at least one style or reference image.
- Consider allowing assignment to multiple projects or contexts.

## 2. CharacterStyle

**Purpose**: Named style variation for a character’s visual appearance.
**Fields**:

- `character` (CharacterProfile FK)
- `style_name`
- `prompt_helper` (PromptHelper FK)
- `prompt`, `negative_prompt`
- `image_reference`
- `created_at`

**Relations**:

- FK → `CharacterProfile` (`styles`)
- FK → `images.PromptHelper` (`prompt_helper`)

**Notes & Improvements**:

- Validate that either `prompt` text or `prompt_helper` is provided.
- Ensure `negative_prompt` defaults from helper when blank.
- Store and index image metadata (dimensions, format).
- Add index on `style_name` for quick lookups.

## 3. CharacterReferenceImage

**Purpose**: Stores reference images for a character with metadata and tags.
**Fields**:

- `character` (CharacterProfile FK)
- `image`
- `caption`, `alt_text`
- `created_at`
- M2M `tags` (images.TagImage)
- `style` (PromptHelper FK)
- `is_primary`

**Relations**:

- FK → `CharacterProfile` (`reference_images`)
- M2M → `images.TagImage` (`tags`)
- FK → `images.PromptHelper` (`style`)

**Notes & Improvements**:

- Enforce a single `is_primary` image per character via DB constraint.
- Auto-generate thumbnails and web-optimized variants.
- Allow ordering of multiple reference images.
- Validate `alt_text` length for accessibility.

## 4. CharacterTag

**Purpose**: Allows tagging characters for grouping or search.
**Fields**:

- `name` (unique)
- M2M `characters` (CharacterProfile)

**Relations**:

- M2M → `CharacterProfile` (`characters`)

**Notes & Improvements**:

- Support hierarchical tags or categories.
- Add optional `description` and UI metadata (color, icon).

## 5. CharacterTrainingProfile

**Purpose**: Tracks embedding/training status for characters.
**Fields**:

- `character` (OneToOne CharacterProfile FK)
- `embedding` (JSON)
- `status` (pending/training/complete/failed)
- `task_id`
- `created_at`, `updated_at`

**Relations**:

- One-to-one → `CharacterProfile` (`training_profile`)

**Signals**:

- `post_save` on `CharacterProfile` auto-creates a training profile.

**Notes & Improvements**:

- Normalize embedding storage (e.g., blob or external store).
- Track training start/end timestamps and logs.
- Link to training job records for error diagnostics.

---

# Cross-Model Connections & Gaps

- **Profile ↔ Style**: clear one-to-many from `CharacterProfile` to `CharacterStyle`.
- **Profile ↔ ReferenceImage**: direct FK relationship.
- **Profile ↔ TrainingProfile**: auto-created on save.
- **Profile ↔ Tags**: many-to-many for grouping.
- **Styles & Images ↔ PromptHelper**: both reference `images.PromptHelper`, consider unifying visual style concept.
- **No chat-session linkage**: characters aren’t connected to assistant sessions or memory entries.
- **Ownership audit**: has `created_by` but no `updated_by` or change log.

# Summary of Recommended Improvements

1.  Enforce single primary reference image per character with a DB constraint.
2.  Add ordering and metadata (dimensions, formats) for styles and reference images.
3.  Strengthen `slug` management, re-slug on name changes, and backfill existing data.
4.  Extend `CharacterTag` with hierarchy and metadata.
5.  Enhance `CharacterTrainingProfile` with detailed logs, timestamps, and error relations.
6.  Consider linking characters to chat sessions, memory entries, or usage analytics for richer context.
