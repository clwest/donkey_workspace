from django.urls import reverse, resolve
from django.test import SimpleTestCase


class ImagesRoutingTests(SimpleTestCase):
    """Verify images URLs are registered in the main router."""

    def test_images_router_connected(self):
        url = reverse("images-list")
        # Should resolve to the ImageViewSet list action under /api/images/
        self.assertEqual(url, "/api/images/images/")
        resolver = resolve(url)
        self.assertEqual(resolver.view_name, "images-list")
