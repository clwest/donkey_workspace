# 🔄 Route Sync Checklist

Use this short list to confirm that React routes point at the right backend URLs.

1. Run `python manage.py show_urls` (or inspect `urls.py`) to see all API paths.
2. Review `src/App.jsx` and pages under `src/pages/` to note every React route.
3. For each route, confirm any `fetch` or `apiFetch` call uses the matching backend endpoint.
4. Check that path parameters like `:id` or `:slug` match DRF patterns in the backend.
5. Document any mismatches and update routes or aliases so navigation and API calls stay in sync.
