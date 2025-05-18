"""
Defines preset image generation styles with corresponding image paths and style-enhancing prompt suffixes.
Paths are dynamically built from BASE_URL configured in settings.
"""

from django.conf import settings

BASE = getattr(settings, "BASE_URL", "http://localhost:8000")

prompt_presets = {
    "Cinematic": {
        "category": "Realistic & Cinematic",
        "description": "High-budget cinematic stills with a dramatic and emotional tone. Great for story openers or climactic scenes.",
        "prompt": "cinematic still, emotional atmosphere, harmonious color palette, vignette lighting, ultra-detailed, high budget look, shallow depth of field, cinemascope aspect ratio, moody ambiance, epic composition, stunning visuals, film grain texture, realistic lighting, bokeh effect",
        "negative_prompt": "blurry, pixelated, cartoonish, low quality, overexposed, poorly lit, watermark, distorted faces, unrealistic anatomy, text artifacts, extra limbs",
        "tags": ["cinematic", "film", "dramatic", "storytelling"],
    },
    "Digital Art": {
        "category": "Digital & Concept Art",
        "description": "Painterly digital style ideal for fantasy or sci-fi storytelling. Popular on concept art platforms.",
        "prompt": "digital artwork, detailed illustration, painterly style, matte painting, ultra-detailed, digital painting, trending on ArtStation, concept art, vibrant colors, high-resolution, professional quality",
        "negative_prompt": "low resolution, blurry, messy brush strokes, childlike drawing, amateur, distorted anatomy, extra limbs, overexposed, pixelated, text artifacts, watermark, signature",
        "tags": ["digital", "concept", "illustration", "fantasy"],
    },
    "Radiant": {
        "category": "Fantasy & Magical",
        "description": "Cosmic, vivid, and dreamlike visuals with strong lighting and mystical vibes. Perfect for magical moments.",
        "prompt": "centered composition, intricate painted details, volumetric lighting, beautiful and vibrant, deep rich colors, masterpiece quality, sharp focus, ultra-detailed, inspired by Dan Mumford and Marc Simonetti, cosmic elements, astrophotography influence, ethereal glow",
        "negative_prompt": "washed out colors, blurry, flat lighting, overexposed, low detail, chaotic background, distorted anatomy, extra limbs, text artifacts, dull, oversaturated, poor composition",
        "tags": ["radiant", "magical", "glow", "cosmic"],
    },
    "Sketch": {
        "category": "Illustration & Drawing",
        "description": "Black-and-white pencil sketch style for a hand-drawn, detailed visual appearance. Great for storyboards or rough outlines.",
        "prompt": "realistic pencil sketch, finely detailed drawing, graphite texture, black and white, shading and depth, hand-drawn style, inspired by Paul Cadden, high contrast lines, subtle pencil gradients",
        "negative_prompt": "color, digital effects, blurry lines, sloppy sketching, low detail, cartoonish, distorted proportions, marker or ink, text, watermark",
        "tags": ["sketch", "black-and-white", "drawing", "pencil"],
    },
    "Photographic": {
        "category": "Realistic & Cinematic",
        "description": "Ultra-realistic cinematic photos using film photography principles. Ideal for grounded, real-world scenes.",
        "prompt": "cinematic photo, 35mm film photography, shallow depth of field, bokeh effect, professional lighting, high-resolution, 4K detail, natural composition, ultra-detailed, soft focus edges, realistic textures, expertly framed shot",
        "negative_prompt": "over-processed, cartoonish, low resolution, digital painting, CGI, unrealistic skin, extra limbs, artifacts, grainy low-quality, watermark, text, distortion",
        "tags": ["photo", "realism", "cinematic", "film"],
    },
    "Funko Pop": {
        "description": "Photorealistic Funko Pop-style character with album cover vibes and crisp product-style lighting.",
        "tags": ["funko", "vinyl", "3d", "collectible"],
        "category": "Character & Toy",
        "prompt": "character as a Funko Pop vinyl figure, photorealistic 3D render, full body shot, highly detailed, studio lighting, collectible toy style, award-winning product photography, crisp textures, featured on Dribbble, styled like an album cover, inspired by Everett Warner",
        "negative_prompt": "realistic human features, horror elements, creepy eyes, low detail, blurry, melted textures, unfinished sculpt, extra limbs, sketch, painterly style, nudity, text, watermark",
    },
    "Concept Art": {
        "description": "A high-detail character design or world-building prompt for cinematic concept sheets and dramatic design.",
        "tags": ["concept", "character", "8k", "artstation"],
        "category": "Concept Art",
        "prompt": "character concept sheet, dynamic concept design, strong contrast, ultra-detailed, 8K resolution, ultra wide-angle shot, pincushion lens distortion, cinematic perspective, trending on ArtStation, inspired by Kim Jung Gi, Zabrocki, Karlkka, and Jayison Devadas",
        "negative_prompt": "unfinished sketch, cartoonish, photorealism, blurry, low resolution, poor anatomy, overly saturated, messy linework, watermark, extra limbs, grayscale",
    },
    "Cyberpunk": {
        "description": "Futuristic cyberpunk aesthetic with neon lights, stylized shadows, and ArtStation-quality digital illustration.",
        "tags": ["cyberpunk", "neon", "futuristic", "scifi", "digital"],
        "category": "Concept Art",
        "prompt": "cyberpunk portrait painting, colorful comic-inspired style, vibrant neon lighting, hyper-detailed, futuristic sci-fi elements, symmetrical composition, sharp focus, smooth textures, Octane render style, HDRI lighting, digital illustration, trending on ArtStation, inspired by Pascal Blanche, Sachin Teng, Sam Yang, and Greg Rutkowski",
        "negative_prompt": "dull colors, low resolution, blurry, realism, grainy textures, distorted anatomy, muted lighting, extra limbs, glitch artifacts, text, watermark",
    },
    "Fantasy": {
        "description": "Colorful and epic fantasy character or creature with high-resolution RPG illustration energy.",
        "tags": ["fantasy", "rpg", "dnd", "magic", "lotr"],
        "category": "Concept Art",
        "prompt": "ultra-detailed fantasy character, full body DnD or Pathfinder portrait, colorful and realistic, intricate design, elegant armor or robes, high-resolution concept art, inspired by Ralph Horsley, fantasy RPG illustration, fanart in the style of LOTR and DnDBeyond, Behance, ArtStation, and DeviantArt quality, HDR render in Unreal Engine 5, cinematic lighting",
        "negative_prompt": "modern clothing, sci-fi elements, low detail, flat colors, blurry, distorted anatomy, cartoon style, overexposed, text, watermark, grayscale, glitch effects",
    },
    "Low Poly": {
        "description": "Minimalist 3D polygon style perfect for mobile games or stylized illustrations. Uses sharp geometric shapes and a clean pastel palette.",
        "tags": ["low poly", "game design", "stylized", "polygon", "minimalist"],
        "category": "Stylized 3D",
        "prompt": "low poly 3D model, minimal detail, sharp geometric shapes, stylized polygon art, clean edges, soft shading, isometric view, pastel color palette, mobile game asset style, flat surfaces, simple environment",
        "negative_prompt": "photorealism, high detail, textures, realistic lighting, smooth surfaces, messy geometry, sketch, text, watermark",
    },
    "Steampunk": {
        "description": "Intricate character designs featuring steam-powered technology and Victorian-inspired fashion. Great for alternate histories or retro-futurism.",
        "prompt": "steampunk character design, Victorian clothing with gears and brass, mechanical accessories, steam-powered tech, goggles, intricate design, concept art style, moody lighting, inspired by Bioshock and Dishonored, detailed illustration",
        "negative_prompt": "modern tech, sci-fi elements, clean minimalism, neon lights, cartoon style, blurry, low resolution, text, watermark",
        "category": "Genre & Setting",
        "tags": ["steampunk", "retro-futurism", "victorian", "concept art", "moody"],
    },
    "Cartoon": {
        "description": "Playful and expressive cartoon-style art with bold lines, saturated colors, and exaggerated features. Works well for children's content and stylized illustrations.",
        "prompt": "cartoon character, bold lines, vibrant colors, exaggerated features, playful expression, clean vector style, character sheet style, modern 2D animation style",
        "negative_prompt": "realism, low contrast, sketchy linework, detailed rendering, grayscale, blurry, extra limbs, text, watermark",
        "category": "Cartoon & Stylized",
        "tags": ["2D", "cartoon", "vector", "playful", "child-friendly"],
    },
    "Post-Apocalyptic": {
        "description": "Gritty survivors in ruined environments, capturing the mood of a post-apocalyptic world. Inspired by Fallout and Mad Max.",
        "prompt": "post-apocalyptic survivor, gritty and worn-out, ruined city background, dark tones, cinematic lighting, dust and debris, scavenger gear, dramatic mood, inspired by Fallout and Mad Max",
        "negative_prompt": "clean clothing, bright colors, futuristic sci-fi, high-tech armor, fantasy elements, blurry, low detail, cartoonish, text, watermark",
        "category": "Genre & Setting",
        "tags": ["gritty", "apocalypse", "survivor", "dust", "dark tones"],
    },
    "Watercolor Dream": {
        "description": "Soft, ethereal painting style that uses pastel tones and brushstroke textures. Ideal for peaceful, dreamlike story moments.",
        "prompt": "soft watercolor painting, dreamy atmosphere, pastel colors, brushstroke texture, subtle gradients, elegant and ethereal, hand-painted style, whimsical composition",
        "negative_prompt": "digital sharpness, vector lines, 3D render, high contrast, harsh shadows, photorealism, text, watermark",
        "category": "Painting Styles",
        "tags": ["watercolor", "dreamy", "ethereal", "soft", "pastel"],
    },
    "Cartoon Animal Stickers": {
        "description": "Cute and simplified cartoon animals with thick outlines, bold colors, and chibi proportions. Designed for sticker sheets or emoji-style reactions.",
        "prompt": "cute cartoon animal sticker, thick outlines, chibi style, kawaii expression, simplified shapes, high contrast, bold color palette, isolated on white background, printable sticker design",
        "negative_prompt": "realistic anatomy, detailed rendering, backgrounds, muted colors, sketch lines, text, watermark",
        "category": "Cartoon & Stylized",
        "tags": ["chibi", "kawaii", "stickers", "animals", "bold lines"],
    },
    "Coloring Page Outline": {
        "description": "Black and white outlines intended for printable coloring pages. Clean line art with no shading or gradients.",
        "prompt": "black and white line art, clean outlines, cartoon-style coloring book page, thick lines, no shading, no color, fun and kid-friendly subject, simplified design, high contrast, monochrome",
        "negative_prompt": "color, gradients, shadows, 3D effects, realistic textures, blurry lines, sketch, text, watermark, soft edges, painting, brush strokes",
        "category": "Line Art & Outlines",
        "tags": ["coloring", "outline", "monochrome", "printable", "kid-friendly"],
    },
    "Roblox": {
        "description": "Blocky 3D characters styled after the Roblox platform. Great for game-inspired illustrations or parody.",
        "prompt": "Roblox-style character, blocky 3D model, simple textures, full body render, colorful avatar, game-ready design, inspired by popular Roblox games, toy-like proportions, studio lighting",
        "negative_prompt": "realistic human features, high detail textures, smooth mesh, soft shading, non-blocky geometry, glitchy output, text, watermark",
        "category": "Game-Inspired",
        "tags": ["blocky", "3D", "avatar", "Roblox", "game art"],
    },
    "Children's Book": {
        "description": "Whimsical and heartwarming hand-drawn illustrations with soft colors and gentle brushwork. Inspired by classic children’s books.",
        "prompt": "storybook illustration, soft colors, gentle brush strokes, whimsical characters, hand-drawn style, watercolor texture, kid-friendly composition, inspired by classic children's books, cozy and magical",
        "negative_prompt": "dark themes, harsh lighting, sketchy lines, realism, overly detailed, adult themes, text, watermark",
        "category": "Storybook & Illustration",
        "tags": ["storybook", "whimsical", "kids", "watercolor", "gentle"],
    },
    "Pixel Art": {
        "description": "Retro-style pixel illustrations in 8-bit or 16-bit aesthetics. Perfect for game sprites or nostalgic artwork.",
        "prompt": "pixel art style, 8-bit or 16-bit character design, retro video game look, blocky shapes, pixelated textures, limited color palette, isometric or side view",
        "negative_prompt": "smooth shading, photorealism, modern 3D graphics, detailed anatomy, blurry, vector lines, text, watermark",
        "category": "Game-Inspired",
        "tags": ["pixel art", "8-bit", "retro", "game", "blocky"],
    },
    "Dark Fantasy": {
        "description": "Grim and moody fantasy artwork featuring gothic environments, medieval elements, and eerie vibes. Perfect for mysterious and dramatic scenes.",
        "prompt": "dark fantasy character, gothic atmosphere, dramatic lighting, medieval armor, eerie environment, inspired by Dark Souls and Elden Ring, ultra detailed, painterly style",
        "negative_prompt": "bright colors, modern clothing, sci-fi tech, cartoon style, blurry, low detail, sketch lines, text, watermark",
        "category": "Fantasy & Sci-Fi",
        "tags": ["gothic", "medieval", "dark", "eerie", "soulslike"],
    },
    "Studio Ghibli": {
        "description": "Soft and nostalgic anime-inspired visuals with watercolor textures and whimsical charm. Inspired by the magical world of Studio Ghibli films.",
        "prompt": "Studio Ghibli style, gentle watercolor texture, anime-inspired, soft lighting, whimsical scenery, warm colors, peaceful and nostalgic tone, expressive characters",
        "negative_prompt": "realistic rendering, harsh lines, low resolution, dark horror style, sketchy art, grayscale, text, watermark",
        "category": "Anime & Manga",
        "tags": ["Ghibli", "watercolor", "nostalgic", "whimsical", "anime"],
    },
    "Mythology": {
        "description": "Epic scenes of gods, legends, and mythological creatures. Classical painting style with symbolic and divine visuals.",
        "prompt": "mythological scene, gods and legends, epic composition, ancient symbolism, divine lighting, classical painting style, heroic figures, celestial background, inspired by Greek and Norse mythology",
        "negative_prompt": "sci-fi, modern outfits, cartoon style, low detail, abstract art, text, watermark",
        "category": "Historical & Classical",
        "tags": ["myths", "legends", "gods", "epic", "celestial"],
    },
    "Isometric UI Style": {
        "description": "Top-down vector illustrations with clean UI elements and modern color palettes. Ideal for app/game UI, infographics, or stylized world-building.",
        "prompt": "isometric illustration, clean UI elements, top-down perspective, vector style, modern color palette, crisp edges, minimal design, game-ready asset layout",
        "negative_prompt": "realism, 3D render, messy perspective, sketch lines, painterly texture, text, watermark",
        "category": "Design & UI",
        "tags": ["isometric", "UI", "vector", "game asset", "infographic"],
    },
    "90s Anime": {
        "description": "Retro anime style with cel-shading, expressive faces, and VHS textures. Channeling the golden age of anime like Cowboy Bebop and Sailor Moon.",
        "prompt": "90s anime style, VHS texture, cel shading, thick outlines, expressive faces, retro color grading, dramatic lighting, vintage anime aesthetic, inspired by Cowboy Bebop and Sailor Moon",
        "negative_prompt": "modern digital art, 3D rendering, realistic proportions, muted tones, sketchy, text, watermark",
        "category": "Anime & Manga",
        "tags": ["retro", "cel-shaded", "anime", "90s", "VHS"],
    },
    "AI Glitch Art": {
        "description": "Surreal, corrupted visuals born from digital distortion and neural noise. Perfect for edgy, abstract, or cyber-experimental scenes.",
        "prompt": "AI glitch art, corrupted pixels, surreal distortion, neural noise, abstract symmetry, chromatic aberration, datamosh aesthetics, neon fragments, digital dreamlike scene",
        "negative_prompt": "clean lines, realism, traditional media, cartoon style, low detail, text, watermark",
        "category": "Abstract & Experimental",
        "tags": ["glitch", "neon", "surreal", "cyber", "experimental", "datamosh"],
    },
    "Magical Girl": {
        "description": "Cute, sparkly, and radiant with transformation magic and glowing accessories. Ideal for whimsical, heroic, and anime-inspired scenes.",
        "prompt": "magical girl character, sparkles, bright pastels, elaborate costume, anime style, cute expression, glowing accessories, transformation aura, inspired by Sailor Moon and Cardcaptor Sakura",
        "negative_prompt": "dark tones, horror themes, realism, gritty textures, sketch, extra limbs, text, watermark",
        "category": "Anime & Manga",
        "tags": ["sparkles", "pastels", "transformation", "anime", "cute", "magical"],
    },
    "Hero Comic Panel": {
        "description": "Bold, dynamic, and full of superhero energy. Perfect for comic-inspired action scenes with dramatic inking and classic comic book flair.",
        "prompt": "comic book panel, superhero pose, dynamic action, bold inking, dramatic shading, colorful costume design, high energy composition, inspired by Marvel and DC styles",
        "negative_prompt": "blurry, painterly, low contrast, realism, pastel tones, sketchy, text (unless part of speech bubble), watermark",
        "category": "Comics & Graphic Novels",
        "tags": [
            "superhero",
            "comic",
            "dynamic",
            "bold lines",
            "DC",
            "Marvel",
            "action",
        ],
    },
    "Children’s Puzzle Book": {
        "description": "Bright, interactive visuals ideal for educational games, early learning, or whimsical challenges. Think preschool books, Highlights-style layouts, and activity pages.",
        "prompt": "children’s puzzle book page, clean vector lines, bright colors, fun and educational style, simplified characters, interactive visual layout, kid-safe content",
        "negative_prompt": "realism, dark themes, complex anatomy, NSFW, sketchy lines, text, watermark",
        "category": "Children’s",
        "tags": [
            "puzzle",
            "educational",
            "kids",
            "interactive",
            "activity",
            "vector",
            "colorful",
        ],
    },
    "Pixar Style Cartoons": {
        "description": "Charming and full of personality. Mimics the vibrant, stylized realism of Pixar characters with big expressive eyes, cinematic lighting, and wholesome vibes.",
        "prompt": "Pixar-style 3D cartoon character, expressive face, big eyes, full body render, clean textures, cinematic lighting, friendly and fun design, stylized realism",
        "negative_prompt": "realistic human proportions, horror elements, gritty style, blurry, sketch, overexposed, text, watermark",
        "category": "Cartoons & Animation",
        "tags": [
            "pixar",
            "3D cartoon",
            "stylized",
            "family friendly",
            "cinematic",
            "render",
        ],
    },
    "EA Sports Style Images": {
        "description": "Bold and action-packed portraits styled like sports video game covers. Great for athletic heroes, competitive themes, and ESPN-level drama.",
        "prompt": "EA Sports-style portrait, ultra-realistic athlete render, dramatic lighting, clean studio backdrop, bold team branding, sharp focus, styled like an NBA 2K or Madden cover, high-definition, action-ready pose",
        "negative_prompt": "cartoon, low resolution, glitch art, vintage photo, sketch, fantasy elements, text, watermark",
        "category": "Realism & Sports",
        "tags": [
            "sports",
            "athlete",
            "realistic",
            "game cover",
            "drama",
            "hd",
            "portrait",
        ],
    },
    "1800s Photography": {
        "description": "A vintage photographic aesthetic mimicking daguerreotypes and early sepia portraits. Ideal for historical characters, westerns, or antique-styled media.",
        "prompt": "1800s-style portrait photograph, sepia tone, antique lighting, shallow depth of field, daguerreotype aesthetic, serious expression, old western clothing, inspired by Billy the Kid photography",
        "negative_prompt": "modern clothing, color, digital effects, high saturation, cartoonish, clean edges, text, watermark",
        "category": "Historical & Classical",
        "tags": [
            "vintage",
            "sepia",
            "portrait",
            "historical",
            "photography",
            "western",
            "1800s",
        ],
    },
    "Colonial Painting": {
        "description": "Classical oil painting style resembling 17th–18th century portraiture. Rich textures and muted tones — perfect for period stories or aristocratic characters.",
        "prompt": "colonial-era oil painting, formal portrait, historical outfit, muted tones, realistic brushwork, classical composition, rich textures, inspired by 17th-18th century artwork",
        "negative_prompt": "modern style, cartoonish, neon colors, surrealism, sci-fi, sketch, digital filter, text, watermark",
        "category": "Historical & Classical",
        "tags": [
            "colonial",
            "oil painting",
            "formal",
            "portrait",
            "historical",
            "brushwork",
            "classical",
        ],
    },
}


def enrich_prompt_tags(base_prompt: str, prompt_helper, mode: str = "append") -> str:
    """
    Combines the user-entered base prompt with the prompt helper style.

    Modes:
    - "append"  → base_prompt + ", " + prompt_helper.prompt
    - "replace" → only prompt_helper.prompt (strict style mode)
    """
    # Ensure base prompt exists
    base = (base_prompt or "").strip()
    # If no helper or helper has no prompt, return base
    helper_prompt = getattr(prompt_helper, "prompt", None)
    if not helper_prompt:
        return base
    helper = helper_prompt.strip()
    if mode == "replace":
        return helper
    # default append
    if base:
        return f"{base}, {helper}"
    return helper


STABILITY_STYLE_PRESETS = [
    "3d-model",
    "analog-film",
    "anime",
    "cinematic",
    "comic-book",
    "digital-art",
    "enhance",
    "fantasy-art",
    "isometric",
    "line-art",
    "low-poly",
    "modeling-compound",
    "neon-punk",
    "origami",
    "photographic",
    "pixel-art",
    "tile-texture",
]


# Optional helper
def enrich_prompt_tags(image, mode="append"):
    # Only enrich prompts if a style is assigned
    if not getattr(image, "style", None) or not getattr(image.style, "name", None):
        return
    # Use the style name to lookup preset
    style_key = image.style.name
    style = prompt_presets.get(style_key)
    if not style:
        return

    if style.get("prompt"):
        if mode == "replace":
            image.prompt = style["prompt"].strip()
        elif style["prompt"] not in image.prompt:
            image.prompt = f"{image.prompt.strip()}, {style['prompt'].strip()}"

    if style.get("negative_prompt") and not image.negative_prompt:
        image.negative_prompt = style["negative_prompt"]

    image.save()


def get_prompt_for_style(style_name: str) -> dict:
    """Returns prompt & negative prompt strings for a given style."""
    return prompt_presets.get(style_name, {"prompt": "", "negative_prompt": ""})
