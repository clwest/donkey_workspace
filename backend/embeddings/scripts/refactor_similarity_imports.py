# refactor_similarity_imports.py

import os
from pathlib import Path

EXCLUDED_DIRS = {"tests", "docs", "__pycache__"}
TARGET_IMPORT = "from embeddings.helpers.helpers_similarity import compute_similarity"
REPLACEMENT_IMPORT = "from embeddings.helpers.helpers_similarity import compute_similarity"

def should_skip(path):
    return any(part in EXCLUDED_DIRS for part in path.parts)

def scan_and_replace(base_dir="."):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = Path(full_path).relative_to(base_dir)

                if should_skip(rel_path):
                    continue

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    print(f"⚠️ Skipped non-UTF8 file: {rel_path}")
                    continue

                if TARGET_IMPORT in content:
                    new_content = content.replace(TARGET_IMPORT, REPLACEMENT_IMPORT)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"✅ Updated import in: {rel_path}")

if __name__ == "__main__":
    print("🔍 Scanning for compute_similarity import replacements...")
    scan_and_replace()