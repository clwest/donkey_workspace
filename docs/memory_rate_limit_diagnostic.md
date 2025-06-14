# Memory Rate Limiting Diagnostic

This document summarizes findings from a review of why `/api/assistants/:slug/memories/` is frequently hit, leading to HTTP 429 responses.

## Affected Route
- **Endpoint**: `/api/assistants/:slug/memories/`
- **View**: `assistant_memories` in `backend/assistants/views/memory.py`【F:backend/assistants/views/memory.py†L121-L131】
- **Rate Limiting**: `_rate_limited(request, f"assistant_memories:{slug}")` enforces a 3‑second window per user【F:backend/assistants/views/memory.py†L121-L126】

## Frontend Usage
Several components call this endpoint directly:
- `AssistantMemoryPanel` loads memories on mount【F:frontend/src/components/assistant/memory/AssistantMemoryPanel.jsx†L18-L26】
- `AssistantDetailPage` fetches memory stats and intro memory, each hitting the same route【F:frontend/src/pages/assistant/common/AssistantDetailPage.jsx†L158-L201】
- `MemoryChainSettingsPanel` loads a short list of memories when project data is available【F:frontend/src/components/assistant/memory_chain/MemoryChainSettingsPanel.jsx†L9-L21】
- `AssistantMemoriesPage` pulls the entire list for dedicated memory browsing【F:frontend/src/pages/assistant/common/AssistantMemoriesPage.jsx†L14-L23】

When these components render simultaneously (e.g., on the dashboard page), multiple fetches execute in parallel. Additional re-renders caused by state updates in `AssistantDetailPage` or `AssistantDiagnosticsPanel` trigger these hooks again, leading to repeated identical requests within a short period and hitting the rate limit.

## Observations
- No pagination or limit parameters are passed, so each request returns the full memory set.
- The backend view applies only basic throttling (3‑second cache-based lock) without per-user quotas.
- Components like `AssistantMemoryPanel` and the memory stats loader do not share results or debounce fetches when state changes.

## Recommendations
1. **Introduce a shared hook** (e.g., `useAssistantMemories`) that caches results and exposes a manual refresh method. Components should subscribe to this hook rather than fetching independently.
2. **Implement cursor or limit parameters** on `/assistants/:slug/memories/` and update components accordingly to avoid large payloads.
3. **Debounce refresh triggers** from diagnostics actions so multiple state updates within a few seconds do not cause redundant requests.
4. **Expand backend rate limiting** using DRF throttling classes or Redis to guard against accidental loops.

These steps should reduce duplicate fetches and prevent 429 errors on the memory endpoint.
