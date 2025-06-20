# 🎨 Prompt Style Review for Storybook Illustration

This document contains a clean, human-editable export of all image generation prompt styles currently in `prompt_helpers.py` and stored in the `PromptHelper` model.

Each entry includes:

- Style Name
- Description _(to be added or improved)_
- Positive Prompt _(used for image generation)_
- Negative Prompt _(used to avoid unwanted visual elements)_
- Suggested Tags _(optional)_
- Status: ✅ Ready / 🛠 Needs Edit / ✏️ Needs Description

---

## 🧾 Style Review Table

### 1. **Cinematic** — 🛠 Needs Description

**Prompt:**

> cinematic still frame, emotionally immersive scene, harmonious color grading, dramatic lighting with vignette shadows, shallow depth of field, ultra-detailed, widescreen composition, film grain texture, moody ambiance, bokeh highlights, dynamic subject placement, high-budget production style

**Negative Prompt:**

> blurry, pixelated, cartoonish, low quality, overexposed, poorly composed, harsh lighting, distorted faces, unrealistic anatomy, text, watermark, flat background, extra limbs

**Description**
A polished, emotionally-driven cinematic style mimicking high-end movie scenes. Ideal for capturing epic moments, intense drama, or emotional stills from a fictional film.

**Suggested Tags:** cinematic, film, photorealism, drama, movie-still, epic, high-resolution

**Voice Style (Optional)**:
narrator_deep (for deep-voiced dramatic reads — we can define this later)

🔍 Justification
• “Cinematic still frame”: Anchors the concept in film.
• “Emotionally immersive”: Emphasizes storytelling.
• “Harmonious color grading”: Film look is heavily color-balanced.
• “Bokeh highlights”: Evokes lens quality, especially important for dreamy or dramatic scenes.
• “High-budget production style”: Distinguishes from amateur or low-quality renderings.
• “Flat background” (negative): Ensures dimensionality and depth.

---

### 2. **Digital Art** — 🛠 Needs Description

**Prompt:**

> professional digital painting, vivid concept art, painterly brush strokes, ultra-detailed illustration, high-resolution, cinematic composition, matte texture, inspired by top ArtStation artists, rich color palette, story-driven visual, 4K fantasy or sci-fi setting

**Negative Prompt:**

> blurry, low resolution, messy brush strokes, amateur style, distorted anatomy, extra limbs, pixelation, overexposure, noisy background, sketchy lines, watermarks, signatures, text artifacts

🧠 Description:

A high-resolution digital painting style ideal for fantasy and sci-fi illustrations. Focuses on cinematic composition, painterly textures, and vibrant, professional-quality concept art. Often seen on ArtStation and in game/movie pre-production artwork.

🎯 Suggested Tags:

["fantasy", "sci-fi", "concept art", "painterly", "professional", "illustration"]

---

### 3. **Radiant** — ✏️ Needs Description

**Prompt:**

> radiant fantasy artwork, centered composition, intricate painted details, ethereal glow, cosmic background, volumetric lighting, sharp focus, vivid color palette, ultra-detailed, masterpiece quality, inspired by Dan Mumford and Marc Simonetti, symmetrical and dreamlike visuals

**Negative Prompt:**

> washed out colors, blurry, flat lighting, overexposed, low detail, poor composition, distorted anatomy, extra limbs, dull tones, messy background, text artifacts, watermark

🧠 Description:

A glowing, epic illustration style focused on luminous lighting, cosmic visuals, and dramatic, centered compositions. Perfect for mythic heroes, celestial themes, and illustrations that need a powerful and uplifting visual impact. Inspired by fantasy concert posters and cosmic surrealism.

🎯 Suggested Tags:

["cosmic", "glow", "fantasy", "ethereal", "vibrant", "illustration"]

---

### 4. **Sketch** — ✅ Ready

**Prompt:**

> realistic pencil sketch, highly detailed graphite drawing, fine line work, strong shading and depth, monochrome artwork, textured paper look, hand-drawn by Paul Cadden, high contrast tones, visible pencil strokes

**Negative Prompt:**

> color, digital effects, sloppy sketching, low detail, cartoonish, blurry lines, distorted proportions, marker or ink, gradients, text, watermark

🧠 Description:

A hand-drawn pencil sketch style that captures intricate textures, precise lines, and a raw artistic essence. Ideal for black-and-white character studies, environment concepts, or emotionally grounded scenes. Inspired by artists like Paul Cadden and classic graphite illustrators.

🎯 Suggested Tags:

["black and white", "pencil", "sketch", "graphite", "line art", "monochrome"]

**Status:** ✅ Ready

---

### 5. **Photographic** — 🛠 Needs Description

**Prompt:**

> cinematic photo, ultra-realistic portrait, 35mm film style, shallow depth of field, bokeh background, soft lighting, natural shadows, high-definition textures, professionally composed, sharp focus, expertly lit studio shot

**Negative Prompt:**

> cartoonish, low resolution, digital painting, CGI, unrealistic skin, distorted anatomy, extra limbs, over-processed, grainy low-quality, text, watermark, artifacts

🧠 Description:

Ultra-realistic imagery mimicking professional photography. Captures the depth and texture of real-life scenes with high-resolution clarity, shallow depth of field, and cinematic lighting. Perfect for cover shots, character portraits, or product-style visuals.

🎯 Suggested Tags:

["photorealistic", "portrait", "realism", "cinematic", "4K", "bokeh"]

✨ Style: Anime

🧠 Description:

A vibrant, high-energy visual style inspired by traditional and modern Japanese animation. Character-driven, expressive, and emotionally engaging, it’s ideal for storytelling with dramatic flair, fantasy themes, or magical adventures.

🎯 Suggested Tags:

["anime", "manga", "vibrant", "character art", "stylized", "expression"]

✅ Final Prompt:

> anime character portrait, expressive anime face, vibrant color palette, highly detailed, studio anime aesthetic, full body render, dynamic pose, soft cell shading, sharp focus, inspired by WLOP, Artgerm, Ilya Kuvshinov, Pixiv contest winner, trending on ArtStation

🚫 Final Negative Prompt:

> realistic style, blurry, western comic style, sketchy linework, distorted anatomy, extra limbs, poorly drawn face, grayscale, nudity, watermark, text

🟩 Style: Minecraft

🧠 Description:

A voxel-based, blocky visual style inspired by the iconic sandbox game. This style embraces simple geometry, pixelated textures, and vibrant lighting, creating instantly recognizable Minecraft-inspired art for characters, creatures, and landscapes.

🎯 Suggested Tags:

["minecraft", "voxel", "pixelated", "blocky", "game-style", "isometric"]
✅ Final Prompt:

> Minecraft-style scene, voxel art, blocky characters and environment, pixel textures, bright lighting, iconic Minecraft aesthetic, in-game perspective, isometric camera angle, inspired by Mojang art style

🚫 Final Negative Prompt:

> realistic models, smooth surfaces, curved lines, high-poly mesh, blurry textures, modern graphics, detailed anatomy, soft shading, text, watermark

🌴 Style: Vaporwave

🧠 Description:

A retro-futuristic aesthetic infused with 80s nostalgia, neon lights, glitch art, and surreal dreamlike visuals. Perfect for generating synth-laced cityscapes, chill characters, or trippy abstract backdrops.

🎯 Suggested Tags:

["vaporwave", "retro", "80s", "neon", "synth", "glitch", "aesthetic"]

✅ Final Prompt:

> vaporwave aesthetic, neon lights, 80s synth style, palm trees, grid horizon, retro-futuristic vibe, purple and pink hues, glitch art, nostalgic visuals, VHS tape texture, dreamy composition

🚫 Final Negative Prompt:

> realism, detailed textures, muted colors, complex anatomy, natural lighting, soft gradients, clean edges, text, watermark

---

🛡️ Style: Fortnite

🧠 Description:

Inspired by the hyper-stylized character art of Fortnite. This style is ideal for bold, full-body renders of game-ready characters with dynamic poses and clean, expressive sculpts.

🎯 Suggested Tags:

["fortnite", "stylized", "game-art", "epic", "battle", "character-skin", "chad"]

✅ Final Prompt:

> Fortnite character skin, full body shot, highly detailed, in-game render, stylized realism, ultra HD, 8K resolution, cinematic pose, inspired by senior character artists, trending on ArtStation and Polycount, clean head sculpt, expressive face and eyes, detailed anatomy, hero-style design, concept art quality
> 🚫 Final Negative Prompt:
> photorealistic style, horror elements, poor anatomy, distorted proportions, blurry, low quality, NSFW, extra limbs, realistic textures, unfinished render, sketch, grayscale, text, watermark

---

🐥 Style: Cartoon Animal Stickers

🧠 Description:

Optimized for super cute, chibi-style animal stickers. Perfect for printable designs, kids’ art, or character sheets. Thick outlines, simplified forms, and poppy colors define this playful aesthetic.

🎯 Suggested Tags:

["chibi", "cute", "animal", "sticker", "kawaii", "cartoon", "kid-friendly"]

✅ Final Prompt:

> cute cartoon animal sticker, thick outlines, chibi style, kawaii expression, simplified shapes, high contrast, bold color palette, isolated on white background, printable sticker design
> 🚫 Final Negative Prompt:
> realistic anatomy, detailed rendering, backgrounds, muted colors, sketch lines, text, watermark, dark tones

---

🎯 Style Name: Funko Pop

🖼 Description:
Stylized 3D render of a character as a Funko Pop vinyl figure. Emphasizes toy-like proportions, exaggerated facial features, and glossy textures that resemble collectible pop culture figurines. Great for turning characters into cute, stylized versions of themselves.

🏷 Suggested Tags:
3D, vinyl figure, stylized, cute, toy, pop culture, collectible, portrait

✅ Final Prompt:

> character as a Funko Pop vinyl figure, photorealistic 3D render, full body shot, highly detailed, studio lighting, collectible toy style, award-winning product photography, crisp textures, featured on Dribbble, styled like an album cover, inspired by Everett Warner
> 🚫 Final Negative Prompt:
> realistic human features, horror elements, creepy eyes, low detail, blurry, melted textures, unfinished sculpt, extra limbs, sketch, painterly style, nudity, text, watermark

---

🎯 Style Name: Concept Art

🖼 Description:
Professional-grade concept design used for character sheets, world-building, and high-impact visuals. Features dramatic contrast, dynamic compositions, and artistic techniques found in AAA video game and film production pipelines.

🏷 Suggested Tags:
concept art, character sheet, cinematic, illustration, AAA quality, ArtStation, high contrast, game dev

✅ Final Prompt:

> character concept sheet, dynamic concept design, strong contrast, ultra-detailed, 8K resolution, ultra wide-angle shot, pincushion lens distortion, cinematic perspective, trending on ArtStation, inspired by Kim Jung Gi, Zabrocki, Karlkka, and Jayison Devadas

🚫 Final Negative Prompt:

> unfinished sketch, cartoonish, photorealism, blurry, low resolution, poor anatomy, overly saturated, messy linework, watermark, extra limbs, grayscale

---

🎯 Style Name: Cyberpunk

🖼 Description:
A vivid and gritty futuristic aesthetic featuring glowing neon lights, high-tech retro flair, and stylized urban sci-fi. Great for dystopian cityscapes, enhanced characters, and night-soaked drama.

🏷 Suggested Tags:
cyberpunk, neon, sci-fi, futuristic, vibrant, concept, digital painting, artstation

✅ Final Prompt:

> cyberpunk portrait painting, colorful comic-inspired style, vibrant neon lighting, hyper-detailed, futuristic sci-fi elements, symmetrical composition, sharp focus, smooth textures, Octane render style, HDRI lighting, digital illustration, trending on ArtStation, inspired by Pascal Blanche, Sachin Teng, Sam Yang, and Greg Rutkowski

🚫 Final Negative Prompt:

> dull colors, low resolution, blurry, realism, grainy textures, distorted anatomy, muted lighting, extra limbs, glitch artifacts, text, watermark

---

🎯 Style Name: Fantasy

🖼 Description:
A high-fidelity fantasy aesthetic perfect for DnD heroes, enchanted creatures, magical realms, and cinematic worldbuilding. Inspired by classic RPG art and modern fantasy illustrations.

🏷 Suggested Tags:
fantasy, DnD, RPG, magic, armor, medieval, concept art, epic, unreal engine

✅ Final Prompt:

> ultra-detailed fantasy character, full body DnD or Pathfinder portrait, colorful and realistic, intricate design, elegant armor or robes, high-resolution concept art, inspired by Ralph Horsley, fantasy RPG illustration, fanart in the style of LOTR and DnDBeyond, Behance, ArtStation, and DeviantArt quality, HDR render in Unreal Engine 5, cinematic lighting
> 🚫 Final Negative Prompt:
> modern clothing, sci-fi elements, low detail, flat colors, blurry, distorted anatomy, cartoon style, overexposed, text, watermark, grayscale, glitch effects

---

🎯 Style Name: Low Poly

🖼 Description:
A stylized minimalist 3D art style using geometric shapes, clean edges, and soft gradients. Great for modern mobile games, ambient landscapes, and charming low-detail characters.

🏷 Suggested Tags:
low poly, minimalist, polygon, 3D model, isometric, stylized, mobile game, vector

✅ Final Prompt:

> low poly 3D model, minimal detail, sharp geometric shapes, stylized polygon art, clean edges, soft shading, isometric view, pastel color palette, mobile game asset style, flat surfaces, simple environment

🚫 Final Negative Prompt:

> photorealism, high detail, textures, realistic lighting, smooth surfaces, messy geometry, sketch, text, watermark

---

🎯 Style Name: Steampunk
🖼 Description:
A retro-futuristic style blending Victorian fashion, brass machinery, steam-powered tech, and a touch of gritty elegance. Ideal for characters, cities, and inventions that feel like they came from an alternate 1800s timeline.

🏷 Suggested Tags:
steampunk, Victorian, gears, brass, alternate history, mechanical, moody, retro-futuristic, concept art

✅ Final Prompt:

> steampunk character design, Victorian clothing with gears and brass, mechanical accessories, steam-powered tech, goggles, intricate design, concept art style, moody lighting, inspired by Bioshock and Dishonored, detailed illustration
> 🚫 Final Negative Prompt:
> modern tech, sci-fi elements, clean minimalism, neon lights, cartoon style, blurry, low resolution, text, watermark

---

🎯 Style Name: Cartoon

🖼 Description:
A clean, colorful, and exaggerated 2D style perfect for lighthearted characters, animated worlds, or playful scenes. Think Saturday morning cartoons, modern vector animation, and stylized expression.

🏷 Suggested Tags:
cartoon, 2D animation, bold lines, playful, colorful, stylized, character design, vector

✅ Final Prompt:

> cartoon character, bold lines, vibrant colors, exaggerated features, playful expression, clean vector style, character sheet style, modern 2D animation style

🚫 Final Negative Prompt:

> realism, low contrast, sketchy linework, detailed rendering, grayscale, blurry, extra limbs, text, watermark

---

⚙️ Style Name: Post-Apocalyptic

💀 Description:
A gritty, worn-down aesthetic soaked in dust, rubble, and survival gear. Perfect for ruined cities, scavenger heroes, radioactive wastelands, and that haunting cinematic glow after the end of the world.

🏷 Suggested Tags:
post-apocalyptic, wasteland, survival, ruins, dust, scavenger, gritty, cinematic

✅ Final Prompt:

> post-apocalyptic survivor, gritty and worn-out, ruined city background, dark tones, cinematic lighting, dust and debris, scavenger gear, dramatic mood, inspired by Fallout and Mad Max
> 🚫 Final Negative Prompt:
> clean clothing, bright colors, futuristic sci-fi, high-tech armor, fantasy elements, blurry, low detail, cartoonish, text, watermark

---

🎨 Style Name: Watercolor Dream

🧚 Description:
Soft, elegant, and ethereal. This style evokes dreamy watercolor paintings with gentle brush strokes, pastel gradients, and an almost magical lightness. Ideal for tender moments, emotional scenes, and whimsical worlds.

🏷 Suggested Tags:
watercolor, pastel, dreamy, ethereal, hand-painted, soft, whimsical, subtle

✅ Final Prompt:

> soft watercolor painting, dreamy atmosphere, pastel colors, brushstroke texture, subtle gradients, elegant and ethereal, hand-painted style, whimsical composition

🚫 Final Negative Prompt:

> digital sharpness, vector lines, 3D render, high contrast, harsh shadows, photorealism, text, watermark

---

🖤 Style Name: Coloring Page Outline

📝 Description:
Clean black-and-white line art with bold outlines and no shading or color. Perfect for printable coloring books or interactive digital pages. This style emphasizes simplicity, clarity, and kid-safe fun — everything needed to bring scenes to life through imagination.

🏷 Suggested Tags:
coloring book, black and white, bold lines, kid-friendly, printable, line art, monochrome, no shading

✅ Final Prompt:

> black and white line art, clean outlines, cartoon-style coloring book page, thick lines, no shading, no color, fun and kid-friendly subject, simplified design, high contrast, monochrome

🚫 Final Negative Prompt:
color, gradients, shadows, 3D effects, realistic textures, blurry lines, sketch, text, watermark, soft edges, painting, brush strokes

---

🟨 Style Name: Roblox

📝 Description:
Inspired by Roblox avatars and game assets, this style delivers blocky 3D models, colorful textures, and toy-like proportions. Great for creating game-ready illustrations, characters, or scenes that match the beloved low-poly sandbox aesthetic.

🏷 Suggested Tags:
roblox, 3D, blocky, low poly, kid-friendly, game asset, avatar, colorful

✅ Final Prompt:

> Roblox-style character, blocky 3D model, simple textures, full body render, colorful avatar, game-ready design, inspired by popular Roblox games, toy-like proportions, studio lighting

🚫 Final Negative Prompt:

> realistic human features, high detail textures, smooth mesh, soft shading, non-blocky geometry, glitchy output, text, watermark

---

📕 Style Name: Children’s Book

📝 Description:
This style is inspired by the timeless charm of classic children’s picture books — soft colors, hand-drawn lines, watercolor textures, and magical worlds. It’s perfect for bringing heartwarming tales and whimsical characters to life in a gentle, storybook-friendly way.

🏷 Suggested Tags:
storybook, watercolor, hand-drawn, whimsical, kids, picture book, gentle, cozy, classic

✅ Final Prompt:

> storybook illustration, soft colors, gentle brush strokes, whimsical characters, hand-drawn style, watercolor texture, kid-friendly composition, inspired by classic children's books, cozy and magical
> 🚫 Final Negative Prompt:
> dark themes, harsh lighting, sketchy lines, realism, overly detailed, adult themes, text, watermark

---

🧱 Style Name: Pixel Art

📝 Description:
This style captures the nostalgic magic of early video game art — think NES, SNES, and arcade classics. Pixel Art uses a limited color palette, clean 8-bit or 16-bit shapes, and low-res charm. Perfect for retro adventures, RPGs, and side-scrolling quests.

🏷 Suggested Tags:
pixel-art, retro, 8bit, 16bit, lowres, blocky, isometric, game-style, arcade, nostalgia

✅ Final Prompt:

> pixel art style, 8-bit or 16-bit character design, retro video game look, blocky shapes, pixelated textures, limited color palette, isometric or side view

🚫 Final Negative Prompt:

> smooth shading, photorealism, modern 3D graphics, detailed anatomy, blurry, vector lines, text, watermark

---

🧛 Style Name: Dark Fantasy

📝 Description:
Grim, gothic, and dripping with atmosphere. The Dark Fantasy style blends medieval aesthetics with eerie environments and dramatic lighting. It’s all about mysterious characters, twisted worlds, and epic moments that feel pulled straight from Dark Souls or Elden Ring.

🏷 Suggested Tags:
dark-fantasy, gothic, medieval, armor, soulslike, eerie, moody, epic, grimdark, magic

✅ Final Prompt:

> dark fantasy character, gothic atmosphere, dramatic lighting, medieval armor, eerie environment, inspired by Dark Souls and Elden Ring, ultra detailed, painterly style

🚫 Final Negative Prompt:

> bright colors, modern clothing, sci-fi tech, cartoon style, blurry, low detail, sketch lines, text, watermark

---

🌼 Style Name: Studio Ghibli

📝 Description:
Soft, whimsical, and emotionally rich, this style captures the charm of hand-drawn anime classics. Think gentle watercolor textures, cozy lighting, and peaceful characters exploring dreamlike landscapes. Inspired by films like My Neighbor Totoro and Spirited Away.

🏷 Suggested Tags:
ghibli, anime, watercolor, nostalgic, whimsical, soft-light, nature, emotion, peaceful

✅ Final Prompt:

> Studio Ghibli style, gentle watercolor texture, anime-inspired, soft lighting, whimsical scenery, warm colors, peaceful and nostalgic tone, expressive characters
> 🚫 Final Negative Prompt:
> realistic rendering, harsh lines, low resolution, dark horror style, sketchy art, grayscale, text, watermark

---

🏛️ Style Name: Mythology

📝 Description:
Epic, timeless, and steeped in grandeur, this style paints scenes like those found on ancient temple walls or classical Renaissance canvases. Expect heroic figures, celestial backdrops, and dramatic lighting inspired by tales of Olympus, Valhalla, and beyond.

🏷 Suggested Tags:
myth, gods, epic, classical, ancient, greek, norse, celestial, heroic, divine-lighting

✅ Final Prompt:

> mythological scene, gods and legends, epic composition, ancient symbolism, divine lighting, classical painting style, heroic figures, celestial background, inspired by Greek and Norse mythology
> 🚫 Final Negative Prompt:
> sci-fi, modern outfits, cartoon style, low detail, abstract art, text, watermark

---

🧩 Style Name: Isometric UI Style

📝 Description:
Clean, minimal, and game-ready. This style is perfect for rendering sleek top-down environments, UI mockups, and scene compositions with modern flat colors and razor-sharp geometry — like a playable Figma prototype.

🏷 Suggested Tags:
isometric, ui, vector, top-down, clean, minimal, flat-color, game-ready, design

✅ Final Prompt:

> isometric illustration, clean UI elements, top-down perspective, vector style, modern color palette, crisp edges, minimal design, game-ready asset layout

🚫 Final Negative Prompt:

> realism, 3D render, messy perspective, sketch lines, painterly texture, text, watermark

---

📼 Style Name: 90s Anime

📝 Description:
Relive the nostalgic charm of retro anime with thick outlines, cel shading, and dramatic lighting. This style captures the expressive, frame-by-frame energy of vintage anime classics from the VHS era — complete with stylized flair and bold color blocking.

🏷 Suggested Tags:
anime, vintage, 90s, cel-shaded, nostalgic, retro, VHS, expressive, stylized

✅ Final Prompt:

> 90s anime style, VHS texture, cel shading, thick outlines, expressive faces, retro color grading, dramatic lighting, vintage anime aesthetic, inspired by Cowboy Bebop and Sailor Moon
> 🚫 Final Negative Prompt:
> modern digital art, 3D rendering, realistic proportions, muted tones, sketchy, text, watermark

---

🧠 Style Name: AI Glitch Art

📝 Description:
Embrace the chaos of neural distortion and surreal abstraction. This style turns digital noise into a masterpiece—perfect for futuristic, otherworldly, or eerie visuals. Think corrupted dreams, glitched realities, and aesthetic errors that somehow just work.

🏷 Suggested Tags:
glitch, surreal, neural, abstract, chaotic, digital, datamosh, experimental, dreamcore, techno-aesthetic

✅ Final Prompt:

> AI glitch art, corrupted pixels, surreal distortion, neural noise, abstract symmetry, chromatic aberration, datamosh aesthetics, neon fragments, digital dreamlike scene
> 🚫 Final Negative Prompt:
> clean lines, realism, traditional media, cartoon style, low detail, text, watermark

---

🧠 Style Name: Magical Girl

📝 Description:
Channel the glitter, drama, and heart of iconic anime heroines. This style brings enchanting transformations, radiant pastels, and fierce-yet-cute energy. Perfect for stories filled with wonder, emotion, and a little cosmic butt-kicking.

🏷 Suggested Tags:
anime, magical, transformation, sparkle, cute, pastel, sailor moon, heroine, light magic, kawaii

✅ Final Prompt:

> magical girl character, sparkles, bright pastels, elaborate costume, anime style, cute expression, glowing accessories, transformation aura, inspired by Sailor Moon and Cardcaptor Sakura

🚫 Final Negative Prompt:

> dark tones, horror themes, realism, gritty textures, sketch, extra limbs, text, watermark

---

🧠 Style Name: Hero Comic Panel

📝 Description:
Bold lines. Epic poses. Explosive action. This style throws you into the heart of a superhero comic universe, with dynamic energy and iconic comic book flair. Ideal for action scenes, heroic entrances, and anything that screams “This looks like a cover!”

🏷 Suggested Tags:
comic, superhero, action, bold, dynamic, inked, cape, powers, DC, Marvel

✅ Final Prompt:

> comic book panel, superhero pose, dynamic action, bold inking, dramatic shading, colorful costume design, high energy composition, inspired by Marvel and DC styles
> 🚫 Final Negative Prompt:
> blurry, painterly, low contrast, realism, pastel tones, sketchy, text (unless part of speech bubble), watermark

---

🧠 Style Name: Children’s Puzzle Book

📝 Description:
This style is all about fun, learning, and exploration. Think clean lines, bright colors, and simplified shapes that spark curiosity. Designed to look like the pages of an educational puzzle or activity book, it’s ideal for hidden object games, matching puzzles, mazes, or visual riddles inside your storybooks.

🏷 Suggested Tags:
puzzle, kids, activity, bright, vector, educational, hidden object, interactive, colorful, child-friendly

✅ Final Prompt:

> children’s puzzle book page, clean vector lines, bright colors, fun and educational style, simplified characters, interactive visual layout, kid-safe content
> 🚫 Final Negative Prompt:
> realism, dark themes, complex anatomy, NSFW, sketchy lines, text, watermark

---

🧠 Style Name: Pixar Style Cartoons

📝 Description:
This style delivers wholesome, 3D animated magic. Inspired by Pixar classics, it features big eyes, expressive faces, and cinematic lighting—perfect for heartwarming moments and character-driven tales like “Dillweed Learns to Fly.”

🏷 Suggested Tags:
Pixar, cartoon, 3D, animated, friendly, family, cinematic, stylized, emotive

✅ Final Prompt:

> Pixar-style 3D cartoon character, expressive face, big eyes, full body render, clean textures, cinematic lighting, friendly and fun design, stylized realism

🚫 Final Negative Prompt:

> realistic human proportions, horror elements, gritty style, blurry, sketch, overexposed, text, watermark

---

🧠 Style Name: EA Sports Style Images

📝 Description:
Step aside LeBron, Dillweed’s about to dunk. This style brings sports cover intensity—sharp focus, action poses, and dramatic lighting like a Madden or 2K game promo. Ideal for scenes where the donkey is absolutely dominating in Donkeyball 2025.

🏷 Suggested Tags:
sports, realism, EA, action, athlete, cover, high-def, modern, heroic

✅ Final Prompt:

> EA Sports-style portrait, ultra-realistic athlete render, dramatic lighting, clean studio backdrop, bold team branding, sharp focus, styled like an NBA 2K or Madden cover, high-definition, action-ready pose
> 🚫 Final Negative Prompt:
> cartoon, low resolution, glitch art, vintage photo, sketch, fantasy elements, text, watermark

---

🧠 Style Name: 1800s Photography

📝 Description:
For stories like Dillweed Rides West, this style captures the sepia-toned, dusty soul of the Old West. Serious poses, vintage lens artifacts, and historical attire make it feel straight out of a Billy the Kid photo album.

🏷 Suggested Tags:
vintage, sepia, cowboy, daguerreotype, old west, serious, historical, portrait

✅ Final Prompt:

> 1800s-style portrait photograph, sepia tone, antique lighting, shallow depth of field, daguerreotype aesthetic, serious expression, old western clothing, inspired by Billy the Kid photography

🚫 Final Negative Prompt:

> modern clothing, color, digital effects, high saturation, cartoonish, clean edges, text, watermark

---

🧠 Style Name: Colonial Painting

📝 Description:
For when Dillweed becomes a founding father—this style is dignified, painterly, and aristocratic. Perfect for museum-quality illustrations with deep textures, formal poses, and period-accurate vibes.

🏷 Suggested Tags:
colonial, historical, painting, oil, portrait, museum, classical, formal, aristocracy

✅ Final Prompt:

> colonial-era oil painting, formal portrait, historical outfit, muted tones, realistic brushwork, classical composition, rich textures, inspired by 17th-18th century artwork
> 🚫 Final Negative Prompt:
> modern style, cartoonish, neon colors, surrealism, sci-fi, sketch, digital filter, text, watermark

---

## 🎨 Prompt Style Categories

| Category                   | Description                                                                                                              |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `Realistic`                | Styles focused on lifelike rendering, photographic quality, and natural lighting. Great for grounded, believable scenes. |
| `Illustration`             | Painterly, artistic visuals. Works well for storybooks, fantasy, concept art.                                            |
| `Cartoon / Stylized`       | Fun, exaggerated visuals. Think bold outlines, vibrant colors, or chibi designs.                                         |
| `Fantasy / Sci-Fi`         | Mythical, otherworldly, or speculative visuals — high detail and magic.                                                  |
| `Retro / Pixel`            | 8-bit, 90s anime, or nostalgic aesthetics with limited palettes or textures.                                             |
| `Gaming / Avatar`          | Inspired by game engines or game-character design (e.g., Fortnite, Roblox).                                              |
| `UI / Puzzle`              | Clean visuals for educational, puzzle book, or isometric scenes.                                                         |
| `Experimental / Abstract`  | Weird, glitchy, dreamlike, or surreal styles meant to break expectations.                                                |
| `Historical / Classic Art` | Inspired by specific eras (e.g., 1800s photography, colonial painting).                                                  |
| `Children’s`               | Whimsical, soft, and safe for younger audiences. Includes coloring books.                                                |
| `Cinematic / Storyboard`   | Wide-angle, cinematic vibes. Ideal for covers, intros, and high-drama pages.                                             |

## 🔧 Next Steps

1. **Edit descriptions** and add any missing tags
2. Mark completed styles as ✅
3. Export reviewed list into `prompt_helpers.py`
4. Re-seed the database from updated data
5. Deploy and test prompt enrichment + generation logic
6. Build prompt debugger interface

Let me know when you're ready to continue reviewing styles or start automating the reseed/debugger part!
