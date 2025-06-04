from pathlib import Path
import traceback

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

        for template_path in self.get_template_sources():
            if exclude_thirdparty and "site-packages" in str(template_path):
                continue
            if folder_filter and folder_filter not in str(template_path):
                continue

            template_name = self.relative_template_name(template_path)
            try:
                template = loader.get_template(template_name)
                template.render(Context({}))
                self.stdout.write(f"✅ {template_path}")
            except Exception:
                self.stderr.write(f"❌ {template_path}")
                self.stderr.write(traceback.format_exc())

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
