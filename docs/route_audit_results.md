# Route Audit Results - Phase Ω.7.1.2

Date: 2025-05-26

## Checklist
1. Attempted to run `python manage.py show_urls` but Django is missing in this environment.
2. Manually reviewed `backend/server/urls.py` to verify endpoints:
   - `/api/assistants/`
   - `/api/codexes/`
   - `/api/ritual-archives/`
   - `/api/agents/` and `/api/swarm/`
   - `/api/cascade/<clause_id>/`
   - `/api/collisions/`
   - `/api/stabilize/`
   - `/api/intel/` and `/api/v1/intel/` (documents, chunks, embeddings)
     - New aliases added: `document-chunks/` and `embedding-metadata/`
3. Checked `frontend/src/App.jsx` routes for matching paths.
4. No stale or missing routes found during manual audit.

## Major Route Coverage

The following table tracks key routes and whether each one has a registered backend endpoint and a visible frontend link. ✅ means the route exists in both places.

| Route | Backend Endpoint? | Frontend Link? |
| ----- | ----------------- | -------------- |
| `/assistants/demo/` | ✅ | ✅ |
| `/assistants/:slug/identity/` | ✅ | ✅ |
| `/assistants/:slug/trust_profile/` | ✅ | ✅ |
| `/assistants/:slug/trail/` | ✅ | ✅ |
| `/assistants/:slug/growth/` | ✅ | ✅ |
| `/assistants/:slug/demo_recap/:session_id/` | ✅ | ✅ |
| `/assistants/:slug/demo_overlay/` | ✅ | ✅ |
| `/assistants/:slug/demo_replay/:session_id/` | ✅ | ✅ |
| `/anchor/symbolic` | ✅ | ✅ |
| `/anchor/mutations` | ✅ | ✅ |
| `/assistants/:slug/reflections` | ✅ | ✅ |
| `/assistants/:slug/replays` | ✅ | ✅ |
| `/assistants/:slug/rag_debug` | ✅ | ✅ |
| `/codex/evolve` | ✅ | ✅ |
| `/dev/route-health` | ✅ | ✅ |

Automated route checks write results to [`route-health-report (1).json`](route-health-report%20(1).json). Example snippet:

```json
{
  "valid_routes": [
    "/login",
    "/register",
    "/logout",
    "/profile"
  ],
  "missing_components": [
    "/assistants/projects/:id",
    "/assistants/:slug",
    "/agents/:slug",
    "/intel/documents/:id"
  ]
}
```

