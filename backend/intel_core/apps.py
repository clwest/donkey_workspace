from django.apps import AppConfig


class IntelCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "intel_core"

    def ready(self):
        from . import signals  # noqa
