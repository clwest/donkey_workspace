ONBOARDING_WORLD = {
    "title": "MythOS Onboarding World",
    "nodes": [
        {"slug": "mythpath", "title": "Choose Mythpath", "description": "Select your mythic path"},
        {"slug": "world", "title": "World Map", "description": "Overview of onboarding"},
        {"slug": "glossary", "title": "Glossary Basics", "description": "Teach your first anchor"},
        {"slug": "archetype", "title": "Archetype Selection", "description": "Pick an archetype"},
        {"slug": "summon", "title": "Summoning Ritual", "description": "Create your assistant"},
        {"slug": "wizard", "title": "Onboarding Wizard", "description": "Guided setup"},
        {"slug": "ritual", "title": "Capstone Ritual", "description": "Complete your training"},
    ],
}

STEPS = [node["slug"] for node in ONBOARDING_WORLD["nodes"]]
