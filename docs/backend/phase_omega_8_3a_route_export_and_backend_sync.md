# 🧠 Phase Ω.8.3.a — Route Audit Download + Backend Sync Overlay

## 🧭 Objective

Expand the `/dev/route-check` page with tools to **export broken routes**, **compare frontend routes to backend API endpoints**, and surface discrepancies Codex can resolve while manual testing happens.

---

## 🛠 Goals

### 🔹 1. Downloadable Route Health Report
- Add a “📥 Download Report” button to `/dev/route-check`
- Export current route status as `.json`:
```json
{
  "valid_routes": [...],
  "missing_components": [...],
  "broken_imports": [...],
  "undefined_backends": [...]
}
```

### 🔹 2. Backend Route Sync
- Ping `/dev/routes` API from this page
- Match frontend route paths to backend API paths
- Highlight:
  - Frontend-only routes (no API)
  - API-only endpoints (no frontend component)
  - Mismatches between expected method/usage

### 🔹 3. Git Commit Badge (Optional)
- Add tooltip showing:
  - `Last touched: git log -n 1 --format="%h %s (%ad)" <file>`

---

## 🔧 Dev Tasks

### Frontend
- [ ] Add export button and JSON stringify logic
- [ ] Add `/dev/routes` fetch + comparison logic
- [ ] Highlight rows based on match status
- [ ] Optional: load Git commit data via `/static/git-meta.json`

### Backend (Optional)
- [ ] Expose `/api/dev/git-route-metadata/` returning route ↔ last edit info

---

## 🧪 Verification

- [ ] Visit `/dev/route-check`
- [ ] Click “Download Report” → verify `.json` structure
- [ ] Load `/dev/routes` ping comparison
- [ ] See rows flagged as:
  - ✅ Matched
  - ❌ Component missing
  - ⚠️ Backend exists, no frontend

---

## 🔁 Related Phases
- Ω.8.3 — Route Verification Console
- Ω.8.2 — Assistant Doc Assignment
- Ω.7.12 — Route Debug / Reload Enforcement

---

## 🧠 TL;DR:
> When Codex generates, this verifies.  
> When you test, this logs.  
> When you’re done — Codex knows what to fix.