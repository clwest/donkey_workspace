#!/usr/bin/env python3
import os, json

def summarize_django_app(app_path):
    summary = {"app": os.path.basename(app_path), "models": [], "views": [], "utils": []}
    for root, dirs, files in os.walk(app_path):
        for fn in files:
            path = os.path.join(root, fn)
            if fn.endswith("models.py"):
                with open(path, encoding="utf-8", errors="ignore") as f:
                    summary["models"] += [line.split("(")[0].strip()
                                          for line in f if line.strip().startswith("class ")]
            if fn.endswith("views.py"):
                with open(path, encoding="utf-8", errors="ignore") as f:
                    summary["views"] += [line.split("(")[0].strip()
                                         for line in f if line.strip().startswith("class ")]
            if fn.endswith(".py") and "utils" in fn:
                summary["utils"].append(os.path.relpath(path, app_path))
    return summary

def summarize_react_components(src_path):
    summary = {"components": [], "hooks": [], "utils": []}
    for root, _, files in os.walk(src_path):
        for fn in files:
            if fn.endswith((".js", ".jsx", ".ts", ".tsx")):
                full_path = os.path.join(root, fn)
                with open(full_path, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "function " in line or "const " in line:
                            if "use" in line and "(" in line:
                                summary["hooks"].append(fn)
                            elif "function " in line or ("const" in line and "=>" in line):
                                summary["components"].append(fn)
                        if "utils" in root:
                            summary["utils"].append(fn)
    return summary

def main():
    root = os.getcwd()
    summaries = {"django_apps": [], "react_modules": {}}

    # Django apps
    backend_path = os.path.join(root, "backend")
    for name in os.listdir(backend_path):
        path = os.path.join(backend_path, name)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "models.py")):
            summaries["django_apps"].append(summarize_django_app(path))

    # React src folder
    frontend_src = os.path.join(root, "frontend", "src")
    if os.path.exists(frontend_src):
        summaries["react_modules"] = summarize_react_components(frontend_src)

    os.makedirs("codex_merge", exist_ok=True)
    with open("codex_merge/app_summaries.json", "w") as outf:
        json.dump(summaries, outf, indent=2)

    print("✅ Generated codex_merge/app_summaries.json")

if __name__ == "__main__":
    main()