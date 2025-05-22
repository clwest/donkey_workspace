import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):
    """Common base class for assistant API tests."""

    def authenticate(self, username: str = "user", password: str = "pw"):
        """Create and authenticate a user for API requests."""
        User = get_user_model()
        user = User.objects.create_user(username=username, password=password)
        self.client.force_authenticate(user=user)
        self.user = user
        return user


__all__ = ["BaseAPITestCase"]
