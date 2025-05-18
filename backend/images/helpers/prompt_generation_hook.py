def prepare_final_prompt(image):
    user_prompt = (image.prompt or "").strip().strip('"')
    negative_prompt = (image.negative_prompt or "").strip()
    style = image.style

    style_prompt = ""
    if style and hasattr(style, "prompt"):
        style_prompt = (style.prompt or "").strip().strip('"')

    # Merge style prompt + user prompt
    if style_prompt and style_prompt not in user_prompt:
        full_prompt = f"{style_prompt}, {user_prompt}"
    else:
        full_prompt = user_prompt
    user_only = user_prompt

    # Enrich with theme prompt if linked to a story with a preset theme
    try:
        # StoryForeignKey on Image model
        story = getattr(image, "story", None)
        if story and getattr(story, "theme_id", None):
            from images.models import ThemeHelper

            theme = ThemeHelper.objects.filter(id=story.theme_id).first()
            if theme and theme.prompt:
                # Append theme prompt
                if theme.prompt not in full_prompt:
                    cleaned_prompt = theme.prompt.strip().strip('"')
                    full_prompt = f"{full_prompt}, {cleaned_prompt}"
                # Merge negative prompts
                neg = theme.negative_prompt or ""
                neg = neg.strip()
                if neg:
                    # Combine existing negative and theme negative
                    parts = [p for p in [negative_prompt, neg] if p]
                    negative_prompt = ", ".join(parts)
    except Exception:
        # If any error, proceed without theme enrichment
        pass
    return full_prompt, user_only, negative_prompt
