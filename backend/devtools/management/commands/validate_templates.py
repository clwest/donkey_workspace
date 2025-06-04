from pathlib import Path
import traceback
import json
import hashlib
from datetime import datetime

from django.core.management.base import BaseCommand
from django.template import Context, loader
from django.template.utils import get_app_template_dirs


class Command(BaseCommand):
    """Render templates to ensure they compile without errors."""

    help = "Validate that all templates can render without exceptions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--exclude-thirdparty",
            action="store_true",
            help="Skip templates from site-packages",
        )
        parser.add_argument(
            "--only-folder",
            type=str,
            help="Restrict checks to a specific folder path",
        )

    def handle(self, *args, **options):
        exclude_thirdparty = options.get("exclude_thirdparty", False)
        folder_filter = options.get("only_folder")

        status_file = Path("logs/template_status.json")
        existing = {}
        if status_file.exists():
            existing = json.loads(status_file.read_text())

        for template_path in self.get_template_sources():
            if exclude_thirdparty and "site-packages" in str(template_path):
                continue
            if folder_filter and folder_filter not in str(template_path):
                continue

            template_name = self.relative_template_name(template_path)
            file_hash = hashlib.sha256(template_path.read_bytes()).hexdigest()
            tag_libraries = []
            for line in template_path.read_text().splitlines():
                if "{%" in line and "load" in line:
                    parts = line.strip().split()
                    if "load" in parts:
                        idx = parts.index("load")
                        tag_libraries.extend(parts[idx + 1 :])
            info = {
                "file_hash": file_hash,
                "last_edited": template_path.stat().st_mtime,
                "last_validated": datetime.utcnow().isoformat(),
                "tag_libraries": tag_libraries,
                "is_rag_linked": "rag" in str(template_path).lower(),
            }
            existing[str(template_path)] = info
            try:
                template = loader.get_template(template_name)
                template.render(Context({}))
                self.stdout.write(f"✅ {template_path}")
            except Exception:
                self.stderr.write(f"❌ {template_path}")
                self.stderr.write(traceback.format_exc())

        status_file.parent.mkdir(parents=True, exist_ok=True)
        status_file.write_text(json.dumps(existing, indent=2))

    def get_template_sources(self):
        directories = set()
        for engine in loader.engines.values():
            directories.update(getattr(engine.engine, "dirs", []))
        directories.update(get_app_template_dirs("templates"))

        for directory in directories:
            path = Path(directory)
            if not path.exists():
                continue
            for file in path.rglob("*.html"):
                yield file

    def relative_template_name(self, path: Path) -> str:
        for engine in loader.engines.values():
            for base_dir in getattr(engine.engine, "dirs", []):
                if str(path).startswith(base_dir):
                    return str(path.relative_to(base_dir))
        for base_dir in get_app_template_dirs("templates"):
            if str(path).startswith(base_dir):
                return str(path.relative_to(base_dir))
        return str(path)
