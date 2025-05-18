 # Videos App Model Overview

 This document walks through the Django model in `videos/models.py`, outlines its fields, relations, and suggests improvement ideas.

 ---

 ## 1. Video

 **Purpose**: Manages video generation requests and stores metadata, files, and external job references.

 **Fields**:
 - `user` (ForeignKey → User): The user who initiated the video generation.
 - `prompt` (TextField): Text prompt or instructions for video generation.
 - `video_url` (URLField, blank/null): URL to the generated video (e.g., CDN link).
 - `video_file` (FileField, blank/null): Uploaded video file stored on the server.
 - `input_image` (ImageField, blank/null): Optional input image for image-to-video tasks.
 - `status` (CharField, choices): Job status (`queued`, `processing`, `completed`, `failed`).
 - `provider` (CharField[50]): Identifier for the generation provider or model (e.g., `runway-gen4`).

 **Connections**:
 - `project` (ForeignKey → project.Project, null/blank): Optional project context.
 - `story` (ForeignKey → story.Story, null/blank): Optional story for which this video is a clip.
 - `paragraph_index` (IntegerField, null/blank): If tied to a specific paragraph or scene index in a story.

 **Metadata**:
 - `caption` (CharField[255], blank/null): Short caption describing the video.
 - `duration_seconds` (FloatField, blank/null): Duration of the generated video in seconds.
 - `thumbnail_url` (URLField, blank/null): URL to a thumbnail image.
 - `video_style` (CharField[100], blank/null): Descriptor for the video style or theme.
 - `output_format` (CharField[20], default=`mp4`): File format of the video.
 - `resolution` (CharField[20], default=`1024x1024`): Target resolution of the video frames.
 - `theme` (CharField[100], blank/null): Free-text theme or category label.
 - `tags` (ArrayField of CharField[50], default=list): List of user-defined tags.

 **Backend & External**:
 - `model_backend` (CharField[50], choices): Backend selection for generation (e.g., Stability.ai, Replicate, OpenAI).
 - `prediction_id` (CharField[255], blank/null): External job identifier for tracking.
 - `error_message` (TextField, blank/null): Captures any error details if job failed.

 **Timestamps**:
 - `created_at` (DateTimeField): Timestamp of request creation.
 - `updated_at` (DateTimeField): Timestamp of last update.
 - `completed_at` (DateTimeField, blank/null): Timestamp when job completed or failed.

 **Meta**:
 - Indexes on `created_at` and `user` for efficient querying by time and user.

 **Notes & Improvements**:
 - Normalize `theme` and `tags` into foreign-key relationships for richer metadata and querying.
 - Add `duration`, `file_size`, and `frame_rate` fields for detailed video analytics.
 - Store `error_message` and `retry_count` to support automatic retries and diagnostics.
 - Enforce cascade or nullification policy for `project` and `story` deletions.
 - Consider adding a `thumbnail_file` (ImageField) for local thumbnail storage.
 - Introduce `priority` or `scheduled_at` fields to manage generation queues.
 - Add `created_by`, `processed_by`, and audit fields for multi-user operations.
 - Implement soft-delete or archival flags to manage storage retention.
 - Validate `resolution` format and provide choices or presets for user selection.

 ---

 # Cross-Model Connections & Gaps

 - **Project & Story**: Videos link to `project.Project` and `story.Story` for content grouping; ensure consistency in foreign key usage.
 - **Media Pipeline**: Integrate thumbnails and video metadata with front-end galleries and consumption endpoints.
 - **Tagging Strategy**: Align with other apps using dedicated tag models instead of raw arrays.
 - **Provider Abstraction**: Abstract provider-specific logic via a service layer to support multiple backends uniformly.

 # Summary of Recommended Improvements

 1. Migrate `theme` and `tags` to dedicated `Theme` and `Tag` models (FK/M2M).
 2. Extend metadata with technical fields (`duration`, `frame_rate`, `file_size`).
 3. Enhance error handling with retry counts and structured error logs.
 4. Add audit and operational fields (`priority`, `processed_by`, `status_history`).
 5. Support soft-delete or storage lifecycle management for generated videos.
 6. Validate and restrict `resolution` and `output_format` to supported options.