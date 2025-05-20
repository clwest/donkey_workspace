import re
from typing import List, Dict

KEYWORDS = {
    "plan": ("task planning", ["planning", "goals"]),
    "schedule": ("task planning", ["planning"]),
    "search": ("web search", ["search"]),
    "data": ("data analysis", ["analysis", "data"]),
    "analyze": ("data analysis", ["analysis"]),
    "email": ("email drafting", ["communication"]),
}


def infer_skills_from_prompt(prompt_text: str) -> List[Dict]:
    text = prompt_text.lower()
    skills = []
    for key, (name, tags) in KEYWORDS.items():
        if re.search(r"\b" + re.escape(key) + r"\b", text):
            skills.append({"name": name, "confidence": 0.9, "tags": tags})
    return skills
