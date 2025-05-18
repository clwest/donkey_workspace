PROMPT_PLACEMENTS = [
    {
        "name": "Image Style Prompt",
        "prompt_type": "image",
        "placement": "append",
        "description": "Appends visual style details to the end of the image generation prompt.",
    },
    {
        "name": "Narration Prompt",
        "prompt_type": "narration",
        "placement": "prefix",
        "description": "Adds tone and character voice guidance at the beginning of narration prompts.",
    },
    {
        "name": "Voice Prompt (TTS)",
        "prompt_type": "voice",
        "placement": "replace",
        "description": "Replaces default TTS style with selected voice style instructions.",
    },
    {
        "name": "Video Scene Prompt",
        "prompt_type": "video",
        "placement": "append",
        "description": "Appends cinematic instructions to generated video scene prompts.",
    },
    {
        "name": "Style Modifier",
        "prompt_type": "style",
        "placement": "append",
        "description": "Used to modify base prompts with selected visual style presets.",
    },
    {
        "name": "Scene Descriptor",
        "prompt_type": "scene",
        "placement": "prefix",
        "description": "Adds descriptive scene setting to enhance prompt grounding.",
    },
]
