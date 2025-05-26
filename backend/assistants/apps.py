from django.apps import AppConfig


class AssistantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "assistants"

    def ready(self):
        from . import signals  # noqa
