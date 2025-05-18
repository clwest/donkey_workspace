# 🧠 backend/AGENTS.md — Django API Tasks

This file tracks backend-specific work for the Donkey AI Assistant system. For repo-wide goals see the root `AGENTS.md` and check `frontend/AGENTS.md` for UI tasks.

## ✅ Completed

- ✅ Implemented `DelegationEvent` model
- ✅ Linked assistants, sessions, and memory via `NarrativeThread`
- ✅ Updated serializers and reflection logging for delegation
- ✅ Merged conflicting migrations and cleaned up Django state
- ✅ Verified database migrations and model relationships
- ✅ Connected assistant bootstrapping with session/project threads

## 🧼 Cleaned Up

- Removed duplicate migration files (`0004_delegation_event`, etc.)
- Cleared invalid pycache files
- Resolved Django settings, import cycles, and migration graph issues
- Standardized ForeignKey definitions with related_name on conflicting models

## 🧠 Current State

The delegation system now tracks:

- Parent assistant
- Spawned child assistant
- Reason, session, and memory that triggered the delegation
- Project and thread propagation
- Reflection summary (manually attached for now)

## 🔧 Next Tasks for Codex

1. **Finish Delegation Logging Workflow**
   - Ensure `spawn_delegated_assistant()` creates a `DelegationEvent`
   - Attach memory, session, parent/child assistant, and reason
   - Include a reflection summary if passed

2. **Add Serializer + API View**
   - Create `DelegationEventSerializer`
   - Add endpoint: `/api/assistants/delegations/recent/` (last 10 events)

3. **Write Tests**
   - `test_delegation_event_creation.py`
   - `test_spawn_delegated_assistant_links_thread.py`

4. **Optional Enhancements**
   - Auto-reflect after delegation and log to parent assistant
   - Create visual diagram of delegation tree
