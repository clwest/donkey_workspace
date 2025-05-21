from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from pathlib import Path
import subprocess

APP_LABEL = 'memory'

class Command(BaseCommand):
    help = 'Check for model usage within the project.'

    def handle(self, *args, **options):
        app_config = apps.get_app_config(APP_LABEL)
        backend_root = Path(settings.BASE_DIR)
        models_file = backend_root / APP_LABEL / 'models.py'
        for model in app_config.get_models():
            name = model.__name__
            result = subprocess.run(
                ['grep', '-R', name, str(backend_root)],
                capture_output=True, text=True
            )
            lines = [l for l in result.stdout.splitlines() if models_file.as_posix() not in l]
            status = 'USED' if lines else 'UNUSED'
            self.stdout.write(f'{name}: {status}')
