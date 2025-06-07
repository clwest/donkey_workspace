ONBOARDING_WORLD = {
    "title": "MythOS Onboarding World",
    "welcome": "Welcome to the MythOS Onboarding World!",
    "nodes": [
        {
            "slug": "mythpath",
            "title": "Mythpath",
            "description": "Define your guiding instinct",
            "emoji": "\U0001f9ed",
            "goal": "Define your guiding instinct",
            "aliases": {
                "fantasy": "Mythpath",
                "plain": "Assistant Role",
            },
        },
        {
            "slug": "world",
            "title": "World Map",
            "description": "Orient your assistant in a domain",
            "emoji": "\U0001f5fa\ufe0f",
            "goal": "Orient your assistant in a domain",
        },
        {
            "slug": "glossary",
            "title": "Glossary",
            "description": "Start teaching key terms",
            "emoji": "\U0001f4d8",
            "goal": "Start teaching key terms",
        },
        {
            "slug": "archetype",
            "title": "Archetype",
            "description": "Pick a behavior/personality profile",
            "emoji": "\U0001f9ec",
            "goal": "Pick a behavior/personality profile",
        },
        {
            "slug": "summon",
            "title": "Summoning",
            "description": "Create your assistant",
            "emoji": "\U0001f300",
            "goal": "Create your assistant",
        },
        {
            "slug": "personality",
            "title": "Personality",
            "description": "Choose avatar and tone",
            "emoji": "\U0001f9e0",
            "goal": "Choose avatar and tone",
        },
        {
            "slug": "wizard",
            "title": "Wizard",
            "description": "Configure advanced skills",
            "emoji": "\U0001f9d9",
            "goal": "Configure advanced skills (optional)",
        },
        {
            "slug": "ritual",
            "title": "Ritual",
            "description": "Final review and launch",
            "emoji": "\U0001fa84",
            "goal": "Final review and launch",
        },
    ],
    "video": None,
}

STEPS = [node["slug"] for node in ONBOARDING_WORLD["nodes"]]
