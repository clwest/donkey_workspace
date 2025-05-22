from django.utils.deprecation import MiddlewareMixin

class ApiVersionWarningMiddleware(MiddlewareMixin):
    """Attach deprecation warning for non-versioned API calls."""

    def process_response(self, request, response):
        path = request.path
        if path.startswith("/api/") and not path.startswith("/api/v1/"):
            response["X-API-Warning"] = "Deprecated endpoint. Use /api/v1/"
        return response
