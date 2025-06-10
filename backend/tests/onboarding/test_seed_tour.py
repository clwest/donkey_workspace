import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.core.management import call_command
from accounts.models import UserTourCompletion
from django.contrib.auth import get_user_model


def test_seed_tour_completions():
    call_command("seed_tour_completions")
    User = get_user_model()
    user = User.objects.get(username="seed_user")
    assert UserTourCompletion.objects.filter(user=user).exists()
