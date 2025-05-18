# scripts/run_codex_tasks.py

import os
from openai import OpenAI

from codex_tools.codex_helpers import (
    FileCache,
    DuplicatePatchDetector,
    patch_monitor,
    apply_diff,
    make_unified_diff,
)

client = OpenAI()
MODEL = "gpt-4o-mini"
MAX_DIFF_TOKENS = 256

# Initialize your helpers
cache = FileCache()
dup_detector = DuplicatePatchDetector()


def generate_patch(path: str, instruction: str) -> str:
    """
    1) Reads the current file from disk
    2) Prompts Codex to produce a unified diff that satisfies `instruction`
    3) Returns the diff text
    """
    original = cache.read(path)

    prompt = (
        f"### Instruction:\n"
        f"{instruction}\n\n"
        f"### File path: {path}\n\n"
        f"### Current content:\n"
        f"{original}\n\n"
        f"### Please output a unified git diff (with a/{path} and b/{path} headers) "
        f"that implements the above instruction and nothing else.\n\n"
        f"### Diff:\n"
    )

    resp = client.responses.create(
        model=MODEL,
        prompt=prompt,
        max_tokens=MAX_DIFF_TOKENS,
        temperature=0,
        top_p=1,
        n=1,
        stop=None,
    )
    diff_text = resp.choices[0].text.strip()
    return diff_text


@patch_monitor(task_name="update_theme_helpers", intent="Add is_active field")
def patch_theme_helpers():
    path = "images/models.py"
    orig = cache.read(path)

    # 1) Check if it's already there
    if "is_active" in orig:
        print("🚫 Already applied, skipping.")
        return ""

    # 2) Build the modified text by inserting our line
    lines = orig.splitlines(keepends=True)
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith("description"):
            new_lines.append(
                "    is_active = models.BooleanField(\n"
                "        default=True,\n"
                '        help_text="Enable/disable this theme."\n'
                "    )\n"
            )
    modified = "".join(new_lines)

    # 3) Generate a proper diff
    diff = make_unified_diff(path, orig, modified)

    # 4) Skip duplicates
    if dup_detector.is_duplicate(diff):
        print("🚫 Duplicate patch skipped.")
        return ""

    # 5) Apply it
    apply_diff(diff)
    return diff


if __name__ == "__main__":
    patch_theme_helpers()
