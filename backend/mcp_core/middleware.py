from django.utils.deprecation import MiddlewareMixin


class APIVersionDeprecationMiddleware(MiddlewareMixin):
    """Add deprecation warning header for unversioned API requests."""

    def process_response(self, request, response):
        if request.path.startswith("/api/") and not request.path.startswith("/api/v1/"):
            response["X-API-Warning"] = "Deprecated API version; use /api/v1/"

        return response
