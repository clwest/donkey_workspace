# Reflective Ingest Review Flow

```mermaid
flowchart TD
  A[User uploads a document<br>(PDF, YouTube, URL, Text)] --> B[Ingests via /api/intel/ingest]
  B --> C{Was assistant_id provided?}

  C -- No --> Z[Reject or queue for manual review]

  C -- Yes --> D[Store Document<br>+ Chunk + Embed]
  D --> E[Link Document + Chunks<br>to Assistant.memory_context]

  E --> F[Notify Assistant: "New Knowledge Available"]
  F --> G[/assistants/:id/review-ingest/:doc_id/]

  G --> H[Assistant loads top N<br>related chunks via vector search]
  H --> I[Runs reflection via AssistantReflectionEngine]
  I --> J{Insight Type?}

  J -- New Knowledge --> K[Summarize as MemoryEntry<br>+ Add Tags + Chunk Links]
  J -- Agent Proposal --> L[Create Agent<br>+ Assign to Project<br>+ Generate Task]
  J -- Irrelevant --> M[Log and archive]

  K --> N[Surface in AssistantDashboard memory view]
  L --> N
  M --> N
```
