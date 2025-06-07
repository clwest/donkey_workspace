import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status


class AuthFlowTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.username = "authuser"
        self.password = "testpass"
        User.objects.create_user(username=self.username, password=self.password)

    def test_login_and_refresh(self):
        resp = self.client.post(
            "/api/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        access = data["access"]
        refresh = data["refresh"]

        resp = self.client.post("/api/token/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data2 = resp.json()
        self.assertIn("access", data2)
        self.assertNotEqual(access, data2["access"])

    def test_unauthorized_access(self):
        resp = self.client.get("/api/v1/assistants/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
