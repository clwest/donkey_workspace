# 📸 Connecting Media Apps to the Frontend

This guide outlines the steps required to hook up the backend `images`, `characters`, and `story` apps to the React frontend.

## 1. Verify API routes

Ensure the backend exposes the following endpoints (already present in `server/urls.py`):

- `api/images/` – image generation, editing, and gallery endpoints
- `api/characters/` – character profile CRUD and similarity search
- `api/stories/` – story CRUD and tagging

You can confirm via `python manage.py show_urls`.

## 2. Create API helpers

Add helper functions in `src/utils/apiClient.js` for common operations:

```javascript
export const fetchImages = (params) => apiFetch(`/images/`, { params });
export const generateImage = (payload) =>
  apiFetch(`/images/generate/`, { method: "POST", body: payload });
export const fetchCharacters = () => apiFetch(`/characters/profiles/`);
export const fetchStories = () => apiFetch(`/stories/`);
```

## 3. Add React pages

1. **ImageGalleryPage** – display images returned from `fetchImages()`.
2. **ImageCreatePage** – form to submit prompts to `generateImage()` and show progress.
3. **CharacterListPage** – list character profiles and related images.
4. **StoryListPage** – list stories and link to storyboard events.

Place pages under `src/pages/media/` and register them in `App.jsx` with routes such as `/images`, `/images/new`, `/characters`, and `/stories`.

## 4. Update Navbar links

Add navigation links to the new pages so users can access media features easily.

## 5. Display generated media

Use standard `<img>` tags for `output_url` fields. For stories with linked images or videos, show them in the existing `StoryboardEditorPage`.

## 6. Keep routes synced

Run through `../../docs/route_sync_checklist.md` after wiring the new pages to ensure API and React routes stay aligned.

