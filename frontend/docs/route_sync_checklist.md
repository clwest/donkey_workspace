# 🔄 Route Sync & Audit Checklist

This checklist is used to sync backend API routes with frontend React routes and ensure smooth navigation and integration across the system.

---

## ✅ 1. API Endpoint & Frontend Fetch Alignment

- [ ] Verify each `fetch()` call matches the actual `urls.py` path
- [ ] Fix any outdated API paths in React components (e.g. `/api/assistants/:slug/memories/` vs `/api/memory/assistants/:slug/memories/`)
- [ ] Add alias routes in `urls.py` if needed to maintain backwards compatibility

---

## ✅ 2. Normalize Backend Route Naming

Ensure REST-style routes are consistent:

- [ ] `GET /memory/` — List memories
- [ ] `POST /memory/` — Create memory
- [ ] `GET /memory/:id/` — Retrieve memory
- [ ] `PATCH /memory/:id/` — Update memory
- [ ] `DELETE /memory/:id/` — Delete memory
- [ ] Use hyphen-case or snake_case consistently (`reflect-on-memories` vs `reflect_on_memories`)

---

## ✅ 3. Create Dev Route Debug Tool

- [ ] Add `/dev/routes` frontend page
- [ ] List all React routes in a readable table
- [ ] List all API routes pulled from DRF schema or manual export
- [ ] Add “Ping” button next to each API to test status (200/404/etc.)
- [ ] Include working link to navigate to each React route for visual check

---

## ✅ 4. React Route Cleanup & Refactor

- [ ] Ensure all routes declared in `App.jsx` exist and are linked in UI
- [ ] Move any deeply nested files like `pages/memories/entries/MemoryEntryCreatePage.jsx` if needed
- [ ] Confirm route names match in `Route path=...` and `Link to=...`
- [ ] Prefer route structure:  
      `/memories/` → list  
      `/memories/new` → create  
      `/memories/:id` → detail

---

## ✅ 5. End-to-End Assistant Workflow Tests

Test each major assistant flow:

- [ ] Create a new Assistant
- [ ] Add Memories linked to the Assistant
- [ ] View Assistant-linked memories at `/assistants/:slug/memories`
- [ ] Reflect on selected memories
- [ ] Save a new ReflectionLog
- [ ] Link memory to project
- [ ] View all linked memory chains and insights

---

## ✅ 6. Final Checks

- [ ] Make sure `urls.py` in each app (`assistants`, `memory`, `mcp_core`, etc.) is properly nested in `server/urls.py`
- [ ] Confirm `/api/*` route prefixes are consistent
- [ ] Document custom endpoints with nonstandard behavior (e.g. reflection summary generation)

---

🧠 **Pro Tip:** Add a script to dump all registered Django URLs for faster debugging:

```bash
python manage.py show_urls
```
