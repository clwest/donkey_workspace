import os
import ast
import json

IGNORED_DIRS = {"__pycache__", "migrations", "tests"}

VECTOR_FIELDS = {"VectorField", "PGVectorField"}


def extract_model_info(file_path):
    models = []
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            node = ast.parse(f.read(), filename=file_path)
            for class_def in [n for n in node.body if isinstance(n, ast.ClassDef)]:
                fields = []
                for stmt in class_def.body:
                    if isinstance(stmt, ast.Assign):
                        target = stmt.targets[0]
                        if isinstance(target, ast.Name):
                            field_type = getattr(getattr(stmt.value, 'func', None), 'id', '')
                            if field_type:
                                fields.append({"name": target.id, "type": field_type})
                models.append({"name": class_def.name, "fields": fields})
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    return models


def scan_backend_apps(base_path):
    app_summaries = []
    for app in os.listdir(base_path):
        app_path = os.path.join(base_path, app)
        if not os.path.isdir(app_path):
            continue
        summary = {
            "app": app,
            "models": [],
            "views": [],
            "utils": [],
            "embedding": False,
            "reflection": False,
            "rag": False,
            "glossary": False,
        }

        for root, dirs, files in os.walk(app_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for fn in files:
                path = os.path.join(root, fn)
                rel_path = os.path.relpath(path, app_path)

                if fn == "models.py":
                    models = extract_model_info(path)
                    summary["models"].extend(models)
                    for m in models:
                        if any(f['type'] in VECTOR_FIELDS for f in m['fields']):
                            summary["embedding"] = True

                elif "reflection" in rel_path:
                    summary["reflection"] = True
                elif "glossary" in rel_path:
                    summary["glossary"] = True
                elif "rag" in rel_path or "retrieval" in rel_path:
                    summary["rag"] = True

                elif fn.endswith("views.py"):
                    summary["views"].append(rel_path)
                elif fn.endswith("utils.py") or "utils/" in rel_path:
                    summary["utils"].append(rel_path)

        app_summaries.append(summary)
    return app_summaries


def main():
    root = os.getcwd()
    backend_path = os.path.join(root, "backend")
    output_dir = os.path.join(root, "codex_merge")
    os.makedirs(output_dir, exist_ok=True)

    summaries = scan_backend_apps(backend_path)
    with open(os.path.join(output_dir, "app_summaries_v2.json"), "w") as f:
        json.dump(summaries, f, indent=2)

    print("✅ Generated codex_merge/app_summaries_v2.json")


if __name__ == "__main__":
    main()