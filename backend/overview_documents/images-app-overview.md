# Images App

## Models

### Image

    - user `fk users`
    - title
    - description
    - prompt
    - negative_prompt
    - applied_prompt_suffix
    - aspect_ration
    - width
    - height
    - num_outputs
    - steps
    - guidance_scale
    - seed
    - engine_used
    - model_used
    - scheduler
    - style `fk PromptHelper`
    - is_favorite
    - status
    - file_path
    - output_url (urlfield)
    - output_urls (JsonField)
    - error_message
    - created_at
    - updated_at
    - completed_at
    - alt_text
    - caption
    - is_public
    - generation_type
    - model_backend
    - prediction_id
    - was_upscaled
    - was_edited
    - project `fk Project`
    - project_image `fk ProjectImage`
    - story `fk story.Story`
    - character `fk CharacterProfile`
    - order
    - tags `M2M mcp_core.Tag`

### SourceImage

    - user `fk User`
    - image_file
    - title
    - description
    - tags `M2M TagImage (needs to be updated to mcp_core.Tag)`
    - purpose
    - is_public
    - updated_at

### UpscaleImage

    - aspect_ratio
    - request `fk Image`
    - user `fk Users`
    - engine
    - upscale_type
    - output_url
    - created_at

### Edit

    - request `FK Image`
    - user `FK Users``
    - edit_type
    - prompt
    - negative_prompt
    - seed
    - creativity
    - output_format
    - style-_preset
    - output_url
    - created_at

### PromptHelper

    - name
    - description
    - prompt
    - negative_prompt
    - category
    - tags (currently JSONField, may need to be moved to fk or m2m?)
    - is_builtin
    - is_fork
    - parent `fk "self"`
    - is_favorited
    - image_path
    - favorited_by `m2m users`
    - placements `m2m PromptPlacement`
    - voice_style
    - created_by `fk Users`
    - created_at
    - style_preset
    - current_version `fk PromptHelperVersion`

### PromptPlacement

    - name
    - prompt_type
    - placement
    - is_enabled
    - description
    - created_at

### TagImage

    - name (Move to mcp core tags?)

### ThemeFavorite

    - user `fk users`
    - theme `fk ThemeHelper`
    - created_at

### ProjectImage

    - name
    - user `fk users`
    - description
    - slug
    - is_published
    - is_featured
    - created_at

### StableDiffusionUsageLog

    - user `fk users`
    - image `fk images`
    - estimated_credits_used
    - created_at

### PromptHelperVersion

    - helper `fk PromptHelper`
    - version_number
    - prompt
    - negative_prompt
    - notes
    - created_at

### ThemeHelper

    - name
    - description
    - prompt
    - negative_prompt
    - category
    - tags (JSONField)
    - recommended_styles `m2m PromptHelper`
    - is_builtin
    - is_public
    - is_fork
    - parent `fk "self"`
    - created_by `fk Users`
    - created_at
    - updated_at
    - is_featured
    - is_active
    - preview_image

## helpers/download_utils.py

    -
