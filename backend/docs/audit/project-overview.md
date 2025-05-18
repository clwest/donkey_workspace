# Project App Overview

## Core Models
- **Project**: Generic project entity linked to a user. May reference an `Assistant` and an `AssistantProject`. Tracks tasks, milestones, dev docs, and status.
- **ProjectTask**: Individual task with status and priority.
- **ProjectMilestone**: Milestones with due dates.
- **ProjectMemoryLink**: Links a project to `MemoryEntry` instances with a reason.

## Serializers
- `ProjectSerializer`, `ProjectTaskSerializer`, `ProjectMilestoneSerializer`, `ProjectMemoryLinkSerializer`.

## Views & Endpoints
- `ProjectViewSet` registered under `/projects/` provides CRUD operations.
- Nested routes for project stories also defined in `urls.py`.

## Dependencies
- Relies on `assistants` for assistant associations and on `memory` for linked memories.
- Dev docs via `mcp_core.DevDoc` many-to-many.
