 # Trainers App Model Overview

 This document walks through each Django model in `trainers/models.py`, outlines their purposes, fields, relations, and suggests improvement ideas.

 ---

 ## 1. ReplicateModel

 **Purpose**: Defines available external models (via Replicate.ai) that can be used for training or inference within the application.

 **Fields**:
 - `name` (CharField[255]): Human-readable model name (e.g., "stable-diffusion").
 - `version` (CharField[255]): Model version identifier (e.g., "v1.0").
 - `description` (TextField, blank/null): Optional model description or metadata.
 - `is_active` (BooleanField): Flag to enable or disable usage of this model.
 - `created_at` (DateTimeField): Timestamp when the model entry was created.

 **Relations**:
 - One-to-many → `ReplicatePrediction` via the `predictions` related name.

 **Notes & Improvements**:
 - Add a unique constraint on `(name, version)` to prevent duplicate entries for the same model.
 - Include `updated_at` to track modifications to model metadata.
 - Add fields for model parameters or capabilities (e.g., supported input types, default hyperparameters).
 - Index on `is_active` and `name` for efficient filtering of available models.
 - Consider linking to a model registry or URL for documentation and version tracking.

 ---

 ## 2. ReplicatePrediction

 **Purpose**: Records individual prediction jobs submitted to a `ReplicateModel`, capturing input prompts, status transitions, and output references.

 **Fields**:
 - `user` (ForeignKey → User): The user who initiated the prediction.
 - `model` (ForeignKey → ReplicateModel): The external model used for this prediction.
 - `prediction_id` (CharField[255], unique): Identifier returned by the external service.
 - `prompt` (TextField): Input prompt or parameters sent to the model.
 - `status` (CharField[20], choices): Current job status (`starting`, `processing`, `succeeded`, `failed`, `canceled`).
 - `num_outputs` (IntegerField): Number of output items requested.
 - `files` (JSONField, default=list, blank): List of output file URLs or references.
 - `created_at` (DateTimeField): When the job was created in our system.
 - `started_at` (DateTimeField, null/blank): When the external service began processing.
 - `completed_at` (DateTimeField, null/blank): When the job finished or failed.

 **Relations**:
 - FK → `User` via `predictions` related name.
 - FK → `ReplicateModel` via `predictions` related name.

 **Notes & Improvements**:
 - Add a `duration` field (or computed property) to track total runtime (`completed_at - started_at`).
 - Store `error_message` (TextField) to capture failure reasons for diagnostics.
 - Index on `status`, `user`, and `model` to optimize filtering in job dashboards.
 - Consider a JSON schema or typed structure for `files` to include metadata (size, MIME type).
 - Add soft-delete or archival logic for long-running history.
 - Enforce cascade behavior or cleanup of associated output files when predictions are deleted.
 - Track API usage metrics (e.g., tokens used, cost estimate) in dedicated fields.

 ---

 # Cross-Model Connections & Gaps

 - **User Relations**: Predictions are linked to users; ensure consistent naming of related names (e.g., `predictions`).
 - **Model Registry**: `ReplicateModel` acts as a local registry; consider aligning with other service providers (e.g., OpenAI models).
 - **Integration with Trainers Logic**: These models are used by the `trainers` app tasks and serializers; ensure version consistency.
 - **Output Consumption**: For image predictions, relate `files` URLs back to the `images.Image` model or other storage mechanisms.

 # Summary of Recommended Improvements

 1. Enforce `(name, version)` uniqueness and index key fields for performance.
 2. Enhance `ReplicateModel` with metadata about capabilities and parameter schemas.
 3. Add runtime, cost, and error-tracking fields to `ReplicatePrediction` for observability.
 4. Implement cleanup strategies for external artifacts (e.g., file storage TTL or deletion hooks).
 5. Standardize prediction references across different backends (Replicate, OpenAI, etc.) via a generic interface.
 6. Audit predictions with `created_by`, `updated_at`, and versioning for compliance requirements.