# Project App Model Overview

This document walks through the Django model in `project/models.py`, outlines its fields, relations, and suggests improvements.

---

## 1. Project

**Purpose**: Represents a user-owned project with metadata, collaborators, and optional styling for image and narration.

**Fields**:

- `user` (ForeignKey → User): Owner of the project.
- `title` (CharField[255]): Project title.
- `description` (TextField): Optional detailed description.
- `theme` (CharField[100]): Free-text theme label.
- `slug` (SlugField, unique): URL-friendly identifier, auto-generated from `title`.
- `image_style` (CharField[100]): Optional style descriptor (e.g., “Cinematic”).
- `narrator_voice` (CharField[100], choices=[“Echo”, “Nova”]): Voice setting for narration.
- `is_public` (BooleanField): Visibility flag.
- `participants` (ManyToManyField → User): Collaborators on the project.
- `created_at` (DateTimeField): Creation timestamp.
- `updated_at` (DateTimeField): Last modification timestamp.

**Methods**:

- `save()`: Auto-slugifies `title` if `slug` is blank before saving.

**Meta**:

- `ordering`: Sorted by `created_at` ascending.

**Notes & Improvements**:

- **Duplicate Field**: `narrator_voice` is defined twice; remove the redundant declaration.
- **Slug Uniqueness**: Enhance slug logic to handle collisions (e.g., append incremental suffix).
- **Theme Normalization**: Replace free-text `theme` with FK to a `ThemeHelper` or dedicated `Theme` model.
- **Indexing**: Add database index on `slug`, `is_public`, and `created_at` for faster lookups.
- **Participants M2M**: Consider through-model to capture roles (e.g., viewer, editor).
- **Visibility & Access Control**: Integrate with permissions to enforce public/private access.
- **Meta Ordering**: Consider defaulting to `-created_at` (newest first) or including `updated_at`.
- **Serialization**: Add seralizers for user-facing APIs including nested participants.
- **Audit Fields**: Track `created_by`/`updated_by` if different from `user`.

---

# Cross-Model Connections & Gaps

- **Assistant Projects**: The `assistants` app uses its own `Project` model; align naming or integrate with this `Project` model.
- **Memory & Tasks**: Other apps reference a project via free-text or UUID; consider standardizing on this FK.
- **Image & Story**: The `images` and `story` apps link to `Project`; ensure cascade/deletion behavior is intentional.
- **User Relations**: Participants vs. collaborators in other apps; unify roles and related names.

# Summary of Recommended Improvements

1.  Remove duplicate `narrator_voice` field and consolidate choices in one declaration.
2.  Migrate `theme` to a dedicated `Theme` model (with FK) and remove free-text.
3.  Improve slug creation to avoid conflicts and add index on slug.
4.  Enhance `participants` through a role-based join model for richer collaborator metadata.
5.  Standardize project linking across apps by using this `Project` model as the canonical reference.
6.  Add audit and access-control fields to support multi-user workflows.
7.  Adjust default ordering to surface most recent or actively updated projects.
