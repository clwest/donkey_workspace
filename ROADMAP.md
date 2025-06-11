# 🗺️ Unified Roadmap

This roadmap merges short-, mid-, and long-term goals from `GOALS.md` and `FRESH_CHAT_SESSION_NOTES.md`.

## Short-Term Goals
- [ ] Build a diff view for original vs replayed reflections
- [ ] Show term matches/losses (glossary anchors before/after)
- [ ] Tag score delta (summary shift due to replay)
- [ ] Let user mark a reflection as "drifted" or "stabilized"
- [ ] Add Accept/Revert option to reflection replays
- [ ] Add reasoning tag: "Why did reflection change?"
- [ ] Allow mutation suggestions from drifted phrases
- [ ] Add filtering by status: `pending`, `applied`, `rejected`
- [ ] Show fallback count in table
- [ ] Style anchor label vs. suggested label with visual diff
- [ ] Add a CLI to list replay logs by assistant
- [ ] Add `/dev/replays/summary` route with per-assistant diff summary
- [ ] Ensure all `/replays/` pages are indexed in `App.jsx` and the nav
- [ ] Finalize demo-to-real conversion polish
- [ ] Complete onboarding flow (assistant creation via theme)
- [ ] Enable glossary badge assignment + trust panel filtering
- [ ] (bug) Overlay error when anchors undefined (demo)
- [ ] (idea) Add loading spinner on recap views (demo)
- [ ] (bug) Tour button misaligned on mobile (demo)

## Mid-Term Goals
- [ ] Add glossary drift chart per assistant
- [ ] Create Codex panel to view all glossary feedback by term
- [ ] Let assistants propose mutation campaigns based on reflection replays
- [ ] Improve glossary fallback and prompt drift scoring
- [ ] Add skill/tone-based badge unlocks for assistants
- [ ] Add assistant analytics (conversion %, growth %, top anchors)

## Long-Term Goals
- [ ] Open-source model integration via Ollama (Mistral/Phi)
- [ ] Local training loop for prompt boosts, glossary recall, and fallback suppression
- [ ] Auto-eval framework to promote glossary health and reduce drift

## Completed Goals
- [x] RAG reflection replay CLI runs and logs changes
- [x] Glossary mutation suggestions can now be accepted from the UI
- [x] Mutation flow fixed with `suggested_label` syncing and anchor boost logging
- [x] SymbolicGlossaryAnchor metadata enriched with new fields
- [x] Assistant detail now links to `/replays/`, `/anchor/mutations`, `/anchor/symbolic`
- [x] Anchor reinforcement logging tracks positive glossary alignment
- [x] Demo Assistant lifecycle features and endpoints added
- [x] Trust profile endpoint returns detailed metrics
- [x] Trail system shows assistant lifecycle timeline
- [x] Growth stage panel and API endpoints implemented
- [x] Demo prompt boosting tracked and editable
