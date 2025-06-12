# First-Use Tour Troubleshooting

This guide covers common issues with the onboarding tour endpoints.

## Endpoints

- `GET /api/user/` — returns the authenticated user's profile, including `id`.
- `POST /api/users/:id/tours/complete/` — marks the first-use tour as finished.
- `GET /api/assistants/:slug/preview/` — loads a preview when converting demo assistants.

## Symptoms

- A `404 Not Found` error on `/api/users/undefined/tours/complete/` indicates the frontend could not determine the logged-in user ID.
- A `404 Not Found` error on `/api/assistants/<slug>/preview/` may appear if the URL path is missing the slug or if the backend route is misconfigured.

## Fixes

1. Ensure `/api/user/` includes the `id` field. The frontend uses this to construct the tour completion URL.
2. Verify the `assistant-preview` route under `assistants/urls.py` uses `"<slug:slug>/preview/"` so the final path becomes `/api/assistants/<slug>/preview/`.
3. Confirm the assistant slug exists before requesting a preview.
