 # Images App Model Overview

 This document walks through each Django model in `images/models.py`, shows how they relate, and points out gaps or improvement ideas.

 ---

 ## 1. Image

 Purpose: Tracks individual image generation requests and their lifecycle.

 Fields:
 - `user` (FK → User): The requesting user (nullable for system-generated).
 - `title`, `description`: Optional metadata.
 - `prompt`, `negative_prompt`, `applied_prompt_suffix`: Generation inputs.
 - `aspect_ratio`, `width`, `height`: Output dimensions.
 - `num_outputs`, `steps`, `guidance_scale`, `seed`: Generation parameters.
 - `engine_used`, `model_used`, `scheduler`: Runtime selection details.
 - `style` (FK → PromptHelper): Applied prompt style/template.
 - `is_favorite`, `status` (choices: pending, processing, completed, failed).
 - `file_path`, `output_url`, `output_urls`, `error_message`.
 - `created_at`, `updated_at`, `completed_at`.
 - `alt_text`, `caption`: Accessibility fields.
 - `is_public`, `generation_type` (initial/inpaint/variation/remix/scene).
 - `model_backend`, `prediction_id`: External backend and job ID.
 - `was_upscaled`, `was_edited`: Flags for post-processing.
 - `project` (FK → Project), `project_image` (FK → ProjectImage): Organizational linking.
 - `story` (FK → Story), `character` (FK → CharacterProfile).
 - `order`: Sequence index (e.g. page order).
 - `tags` (M2M → TagImage).

 Meta:
 - `ordering`: `-created_at` (newest first).
 - `unique_together`: (`story`, `order`).

 Notes & Improvements:
 - Consider using Django `ContentType`/`GenericForeignKey` for flexible parent linking.
 - Add audit fields (`created_by`, `updated_by`) and optional soft-delete.
 - Index on `status`, `user`, `project` for query performance.

 ---

 ## 2. SourceImage

 Purpose: User-uploaded reference or training images.

 Fields:
 - `user` (FK → User).
 - `image_file` (ImageField).
 - `title`, `description`.
 - `tags` (M2M → TagImage).
 - `purpose` (choices: training, reference, inspiration).
 - `is_public`, `uploaded_at`.

 Notes & Improvements:
 - Validate file size/type and store metadata (dimensions, format).
 - Expose thumbnail or derived versions.

 ---

 ## 3. UpscaleImage

 Purpose: Records upscaling operations performed on an `Image`.

 Fields:
 - `request` (FK → Image), `user` (FK → User).
 - `engine`, `upscale_type` (e.g. conservative, creative, fast).
 - `aspect_ratio` (auto-populated), `output_url`, `created_at`.

 Notes & Improvements:
 - Store source resolution for audit and reproducibility.
 - Consider unifying with `Edit` model for edit operations.

 ---

 ## 4. Edit

 Purpose: Tracks edit actions (inpaint, variation, upscale) on generated images.

 Fields:
 - `request` (FK → Image), `user` (FK → User).
 - `edit_type` (choices), `prompt`, `negative_prompt`, `seed`, `creativity`.
 - `output_format`, `style_preset`, `output_url`, `created_at`.

 Notes & Improvements:
 - Merge with `UpscaleImage` or use common `ImageEdit` base model.
 - Add status field and error logging.

 ---

 ## 5. PromptHelper

 Purpose: Defines prompt “styles” or suffix templates for image (and other) generations.

 Fields:
 - `name`, `description`.
 - `prompt`, `negative_prompt`: Legacy suffix fields.
 - `category`, `tags` (JSON list).
 - `is_builtin`, `is_fork`, `parent` (self-FK).
 - `is_favorited`, `favorited_by` (M2M → User).
 - `image_path` (ImageField), `placements` (M2M → PromptPlacement).
 - `voice_style`, `style_preset` (external API mapping).
 - `created_by`, `created_at`, `current_version` (FK → PromptHelperVersion).

 Meta:
 - `verbose_name`: “Style Prompt Assistant”.
 - `verbose_name_plural`: “Style Prompt Assistants”.

 Methods:
 - `fork(user)`: Clone this style for a new user.

 Notes & Improvements:
 - Deprecate legacy `prompt`/`negative_prompt` in favor of versioned `PromptHelperVersion`.
 - Ensure `current_version` is always populated and remove stray model code in this file.
 - Add `updated_at` and usage counters.

 ---

 ## 6. PromptPlacement

 Purpose: Controls how and where a `PromptHelper` suffix is applied.

 Fields:
 - `name`, `prompt_type` (image, voice, video, narration, style, scene).
 - `placement` (append, replace, prefix), `is_enabled`, `description`, `created_at`.

 Notes & Improvements:
 - Add ordering or scopes for prompt types.

 ---

 ## 7. TagImage

 Purpose: A simple tag model for categorizing images and related entities.

 Fields:
 - `name` (unique).

 Notes & Improvements:
 - Extend with description or tag hierarchy.
 - Consider unifying with other tagging models across apps.

 ---

 ## 8. ThemeFavorite

 Purpose: Tracks favorites of `ThemeHelper` by users.

 Fields:
 - `user` (FK → User), `theme` (FK → ThemeHelper), `created_at`.

 Meta:
 - `unique_together`: (`user`, `theme`).

 Notes & Improvements:
 - Align favoriting patterns with `PromptHelper.is_favorited`.

 ---

 ## 9. ProjectImage

 Purpose: Organizes images into named galleries or “projects”.

 Fields:
 - `name`, `slug`, `description`, `is_published`, `is_featured`, `created_at`.
 - `user` (FK → User).

 Notes & Improvements:
 - Add `updated_at` and owner/team relations.
 - Validate `slug` uniqueness and format.

 ---

 ## 10. StableDiffusionUsageLog

 Purpose: Logs credit/usage metrics for SDXL-based generations.

 Fields:
 - `user` (FK → User), `image` (FK → Image), `estimated_credits_used`, `created_at`.

 Notes & Improvements:
 - Include model, steps, image size for richer analytics.

 ---

 ## 11. PromptHelperVersion

 Purpose: Maintains version history of `PromptHelper` definitions.

 Fields:
 - `helper` (FK → PromptHelper), `version_number`, `prompt`, `negative_prompt`, `notes`, `created_at`.

 Meta:
 - `unique_together`: (`helper`, `version_number`).
 - `ordering`: `-version_number` (latest first).

 Notes & Improvements:
 - Enforce atomic version increments via transactions.
 - Link back to usage logs for each version.

 ---

 ## 12. ThemeHelper

 Purpose: Defines thematic settings (worlds, styles) applied to images and stories.

 Fields:
 - `name`, `description`, `prompt`, `negative_prompt`, `category`, `tags` (JSON).
 - `recommended_styles` (M2M → PromptHelper), `is_builtin`, `is_public`, `is_fork`, `parent`.
 - `created_by`, `created_at`, `updated_at`, `is_featured`, `is_active`, `preview_image`.

 Meta:
 - `ordering`: `name`.

 Notes & Improvements:
 - Versioning for theme changes (similar to `PromptHelperVersion`).
 - Standardize tag representation (JSON vs. M2M).

 ---

 # Cross-Model Connections & Gaps

 - **User Relations**: Many models link to `settings.AUTH_USER_MODEL` for ownership and auditing.
 - **Project/Story/Character**: `Image` bridges across `project`, `story`, and `characters` apps.
 - **Styling vs. Prompting**: Overlap between `PromptHelper`, `ThemeHelper`, and `PromptPlacement`.
 - **Tagging**: Multiple tag patterns (`TagImage`, JSON tags) could be unified.
 - **Versioning**: `PromptHelperVersion` exists, but no version support for `ThemeHelper` or images.
 - **Audit & Metrics**: Usage logs and favoriting patterns are present but inconsistent.

 # Summary of Recommended Improvements

 1. Clean up unintended code sections (e.g., stray model fields under signal handlers).
 2. Consolidate tagging and favoriting approaches across models.
 3. Enrich audit fields (`created_by`, `updated_by`, `status`, `error_message`).
 4. Apply versioning patterns consistently to themes and styles.
 5. Optimize indexing on high-cardinality and frequently queried fields.
 6. Introduce soft-delete or archival flags for lifecycle management.
 7. Consider `GenericForeignKey` for flexible parent/child linking (images, edits, logs).