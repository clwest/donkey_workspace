MUTATION_STYLES = {
    "clarify": {
        "id": "clarify",
        "system_prompt_template": "You are a prompt engineer. Rewrite the following prompt to make it more clear and supportive, preserving the original intent.",
        "description": "Clarify vague or confusing instructions without changing meaning.",
        "tone_options": ["neutral", "playful", "formal"],
    },
    "expand": {
        "id": "expand",
        "system_prompt_template": "You are a prompt engineer. Expand the following prompt with additional helpful context while keeping the same goal.",
        "description": "Add helpful context or examples.",
        "tone_options": ["neutral", "friendly", "formal"],
    },
    "shorten": {
        "id": "shorten",
        "system_prompt_template": "You are a prompt engineer. Shorten the following prompt while keeping the core idea intact.",
        "description": "Make the prompt shorter and more concise.",
        "tone_options": ["neutral", "formal"],
    },
    "formalize": {
        "id": "formalize",
        "system_prompt_template": "You are a prompt engineer. Rewrite the following prompt in a more formal and professional style.",
        "description": "Increase the formality of the wording.",
        "tone_options": ["formal", "neutral"],
    },
    "casualize": {
        "id": "casualize",
        "system_prompt_template": "You are a prompt engineer. Rewrite the following prompt in a casual and relaxed manner.",
        "description": "Make the prompt sound more casual.",
        "tone_options": ["casual", "playful"],
    },
    "convertToBulletPoints": {
        "id": "convertToBulletPoints",
        "system_prompt_template": "You are a prompt engineer. Reformat the following prompt into concise bullet points while keeping all key information.",
        "description": "Reformat as bullet points without losing details.",
        "tone_options": ["neutral", "formal"],
    },
}


def get_style(style_id: str):
    return MUTATION_STYLES.get(style_id)


def list_styles():
    return list(MUTATION_STYLES.values())
