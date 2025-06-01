import os
import json
import time
import hashlib
from functools import wraps
import subprocess
import tempfile
import difflib

# Configuration
DRY_RUN = os.getenv("CODEX_DRY_RUN", "0") in ("1", "true", "yes")
MAX_RETRIES = 3  # Default max retry attempts for patch operations
AVG_TOKENS_PER_LINE = 10  # Rough tokens per line estimate
COST_PER_1K_TOKENS = 0.02  # USD per 1k tokens

# near the top of the file, after imports:
LOG_PATH = os.getenv(
    "CODEX_LOG_PATH", os.path.join(os.getcwd(), "logs", "codex_usage.jsonl")
)


class FileCache:
    """Cache file reads to avoid re-reading unchanged files."""

    def __init__(self):
        self._cache = {}  # filepath -> (mtime, content)

    def read(self, filepath):
        mtime = os.path.getmtime(filepath)
        if filepath in self._cache:
            old_mtime, content = self._cache[filepath]
            if mtime == old_mtime:
                return content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        self._cache[filepath] = (mtime, content)
        return content


class DuplicatePatchDetector:
    """Detect duplicate patch suggestions to avoid reapplying the same fix."""

    def __init__(self):
        self._seen = set()

    def is_duplicate(self, patch_text):
        key = hashlib.sha256(
            patch_text.encode("utf-8", errors="ignore")
        ).hexdigest()
        if key in self._seen:
            return True
        self._seen.add(key)
        return False


def estimate_tokens(lines_count):
    """Estimate tokens based on line count."""
    return lines_count * AVG_TOKENS_PER_LINE


def estimate_cost(tokens):
    """Estimate cost in USD for given tokens."""
    return (tokens / 1000) * COST_PER_1K_TOKENS


class CodexLogger:
    """Log Codex operations to a JSONL file."""

    def __init__(self, log_path=LOG_PATH):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.log_path = log_path

    def log(self, task_name, intent, lines=None, retries=0, success=True, error=None):
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "task": task_name,
            "intent": intent,
            "lines": lines,
            "estimated_tokens": estimate_tokens(lines) if lines is not None else None,
            "cost_usd": (
                round(estimate_cost(estimate_tokens(lines)), 6)
                if lines is not None
                else None
            ),
            "retries": retries,
            "success": success,
            "error": str(error) if error else None,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def patch_monitor(task_name, intent):
    """Decorator to monitor patch operations with retries and logging."""
    logger = CodexLogger()

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if DRY_RUN:
                print(f"[DRY RUN] Would execute {task_name} - Intent: {intent}")
                return None

            retries = 0
            while retries < MAX_RETRIES:
                try:
                    result = fn(*args, **kwargs)
                    lines = result.count("\n") if isinstance(result, str) else None
                    logger.log(
                        task_name, intent, lines=lines, retries=retries, success=True
                    )
                    return result
                except Exception as e:
                    retries += 1
                    logger.log(
                        task_name,
                        intent,
                        lines=None,
                        retries=retries,
                        success=False,
                        error=e,
                    )
                    print(
                        f"[WARN] {task_name} failed attempt {retries}/{MAX_RETRIES}: {e}"
                    )
            print(
                f"[ERROR] {task_name} exceeded max retries ({MAX_RETRIES}). Skipping."
            )
            return None

        return wrapper

    return decorator


def apply_diff(diff_text: str, strip: int = 1):
    """
    Apply a unified-diff string to your repo via the `patch` CLI.
    - `strip` controls how many leading path segments to remove (usually 1).
    """
    # Write diff to a temp file
    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        tf.write(diff_text)
        tf.flush()
        tf_name = tf.name

    # Run `patch -p{strip} -i temp.diff`
    subprocess.run(["patch", f"-p{strip}", "-i", tf_name], check=True)


def make_unified_diff(path: str, original: str, modified: str) -> str:
    """
    Generate a proper unified diff between original and modified text,
    labeling paths as a/{path} and b/{path}.
    """
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
            lineterm="\n",
        )
    )


# Example usage stubs:
#
# cache = FileCache()
# duplicate_detector = DuplicatePatchDetector()
#
# @patch_monitor(task_name='apply_patch', intent='Update theme helper code')
# def apply_patch(patch_text, filepath):
#     if duplicate_detector.is_duplicate(patch_text):
#         print('Duplicate patch detected, skipping.')
#         return None
#     # ... invoke Codex or apply patch logic here ...
#     return patch_text  # or actual diff/patch result
#
# # Enable dry run:
# DRY_RUN = True
# apply_patch('some diff', 'prompt_helpers.py')
