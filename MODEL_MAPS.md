Notes

The repository uses many cross‑app links. Some fields (e.g. ChatSession.assistant) lack a related_name, so reverse access defaults to Django conventions.

The docs mention repairing RAG chunk links and embedding inconsistencies. Those utilities suggest past gaps in content_id or missing memory_context assignments.

Model Relationship Map
Key
FK = ForeignKey
O2O = OneToOneField
M2M = ManyToManyField
RN = related_name

assistants
Model → Related Model Type (RN)
Assistant → prompts.Prompt (system_prompt) FK (assistants_using_prompt)
Assistant → intel_core.Document (documents) M2M (linked_assistants)
Assistant → intel_core.Document (assigned_documents) M2M (assigned_assistants)
Assistant → intel_core.DocumentSet FK (assistants)
Assistant → mcp_core.MemoryContext FK (assistants)
Assistant → assistants.AssistantProject (current_project) FK (active_assistants)
Assistant → tools.Tool (related_tools) M2M (related_tools)
ChatSession → assistants.Assistant FK (chat_sessions)
ChatSession → project.Project FK (chat_sessions)
ChatSession → assistants.AssistantMemoryChain FK (sessions)
StructuredMemory → ChatSession FK (structured_memories)
TokenUsage → ChatSession FK (token_usages)
AssistantChatMessage → ChatSession FK (messages)
AssistantChatMessage → memory.MemoryEntry FK (messages)
intel_core
Model → Related Model Type (RN)
Document → auth.User FK (documents)
Document → mcp_core.MemoryContext FK (documents)
Document → prompts.Prompt (generated_prompt) FK (reflection_documents)
Document → mcp_core.Tag (tags) M2M (document_tags)
DocumentChunk → Document FK (chunks)
DocumentChunk → memory.SymbolicMemoryAnchor (anchor) FK (chunks)
DocumentChunk → EmbeddingMetadata (embedding) O2O (chunk)
DocumentSet → Document M2M (document_sets)
GlossaryUsageLog → assistants.Assistant FK (no RN)
GlossaryUsageLog → DocumentChunk FK (glossary_logs)
memory
Model → Related Model Type (RN)
MemoryEntry → intel_core.Document FK (memory_entries)
MemoryEntry → agents.StabilizationCampaign FK (memory_entries)
MemoryEntry → memory.SymbolicMemoryAnchor FK (memories)
MemoryEntry → project.Project FK (memory_entries)
MemoryEntry → assistants.Assistant FK (memories)
MemoryEntry → assistants.ChatSession FK (chat_entries)
MemoryEntry → agents.Agent M2M (memory_entries)
MemoryEntry → embeddings.Embedding GenericRelation (embeddings)
MemoryEntry → mcp_core.MemoryContext FK (memory_entries)
MemoryChain → MemoryEntry (memories) M2M (chains)
embeddings
Model → Related Model Type (RN)
Embedding → content_object (generic) FK via content_type/object_id
StoryChunkEmbedding → story.Story FK (chunk_embeddings)
StoryChunkEmbedding → mcp_core.Tag (tags) M2M (default RN)
mcp_core
Model → Related Model Type (RN)
Plan → mcp_core.MemoryContext FK (no RN)
Plan → auth.User (created_by) FK (no RN)
Task → Plan FK (tasks)
ActionLog → agents.Agent FK (no RN)
ActionLog → Task FK (no RN)
ActionLog → Plan FK (no RN)
PromptUsageLog → prompts.Prompt FK (usage_logs)
PromptUsageLog → prompts.PromptUsageTemplate FK (usage_logs)
Tag → pgvector.VectorField (embedding) Field for tagging embeddings
NarrativeThread → intel_core.Document M2M (threads)
NarrativeThread → memory.MemoryEntry (origin_memory) FK (origin_threads)
projects
Model → Related Model Type (RN)
Project → auth.User (user) FK (projects)
Project → assistants.Assistant (team) M2M (team_projects)
Project → assistants.AssistantMemoryChain (team_chain) FK (team_projects)
Project → assistants.Assistant (assistant) FK (no RN)
Project → assistants.AssistantProject (assistant_project) FK (linked_projects)
Project → mcp_core.NarrativeThread (narrative_thread) FK (narrative_projects)
Project → mcp_core.DevDoc (dev_docs) M2M (projects)
Project → memory.MemoryEntry (created_from_memory) FK (spawned_projects)
ProjectParticipant → auth.User FK (project_participations)
ProjectParticipant → Project FK (participant_links)
ProjectMemoryLink → Project FK (linked_memories)
ProjectMemoryLink → memory.MemoryEntry FK (default RN)
ProjectMilestone → Project FK (milestones)
ProjectTask → Project FK (core_tasks)
prompts
Model → Related Model Type (RN)
Prompt → mcp_core.Tag M2M (prompt_links)
Prompt → assistants.Assistant FK (linked_prompts)
Prompt → intel_core.Document FK (prompts)
PromptUsageTemplate → prompts.Prompt FK (no RN)
PromptUsageTemplate → assistants.Assistant FK (prompt_templates)
PromptMutationLog → Prompt (original_prompt) FK (mutation_logs)
PromptMutationLog → assistants.Assistant FK (prompt_mutations)
tools
Model → Related Model Type (RN)
ToolUsageLog → tools.Tool FK (logs)
ToolUsageLog → assistants.Assistant FK (no RN)
ToolUsageLog → agents.Agent FK (no RN)
ToolScore → tools.Tool FK (scores)
ToolScore → assistants.Assistant FK (tool_scores)
Data Flow Chain
Document Upload

User calls /api/intel/ingest/ with assistant_id (required) to upload a URL, PDF, YouTube link, or text file.

A Document is created with an optional memory_context pointing to the same context as the assistant.

The document is chunked into DocumentChunk records, each with tokens and metadata.

Each chunk is embedded into EmbeddingMetadata (vectors stored in PGVector).

Linking & Progress

DocumentProgress tracks chunking status and embedding completion.

Chunks link back to their document and optionally a SymbolicMemoryAnchor for glossary usage.

Reflection & Memory

/assistants/:slug/review-ingest/:doc_id/ triggers a reflection run on the document.

The assistant retrieves top chunks via vector search, summarizes them, and saves a MemoryEntry summarizing insights.

AssistantReflectionLog logs the summary, linking to the document chunks and any symbolic anchors.

Embedding & Retrieval

RAGGroundingLog and RAGPlaybackLog capture retrieval details (scores, fallback reason, glossary hits).

During chat, the assistant fetches relevant chunks based on memory_context, glossary scores, and retrieval thresholds.

Chat Session

ChatSession records the conversation; each message becomes an AssistantChatMessage linked to the session and optionally a MemoryEntry.

Token usage is logged per session (TokenUsage).

Memories generated from chat or reflections are accessible through the assistant’s memory_context via assistant.memories.all().

Feedback & Mutation

MemoryFeedback and PromptMutationLog store user feedback or automatic prompt changes.

GlossaryKeeperLog and AnchorReinforcementLog record glossary boost actions, used to adjust retrieval weighting.

Projects & Tasks

Reflections or user interactions may spawn new Project objects or AssistantProject tasks.

ProjectMemoryLink ties key memories to project objectives.

Ongoing Loop

As more documents are ingested and chat sessions evolve, the assistant continues to reflect, mutate prompts, and adjust memory context, enabling a growth loop described in ASSISTANT_LIFECYCLE.md.

Issues / Gaps
Resolved related_name omissions (ChatSession.assistant/project, MemoryEntry.chat_session, PromptUsageTemplate.prompt)

Embedding Reference Breakage

Docs mention repair_rag_chunk_links to fix mismatched content_id fields and missing memory_context assignments.

Suggests older embeddings or chunks might still have inconsistent references.

RAG Retrieval Separation

Embedding (generic embeddings) and EmbeddingMetadata (document chunk vectors) are separate models with no enforced linkage.

Potential confusion when trying to trace an embedding back to its source object.

Orphaned Context

If assistant_id is omitted during ingest, documents may be created without a matching memory_context (see flow diagram).

Leads to manual repair later.

Sparse Indexing

Heavy tables such as MemoryEntry and AssistantChatMessage have limited indexing (only on creation time). Filtering by assistant or thread may be slow.

Proposed Fixes
Add explicit related_name fields

For ChatSession.assistant, ChatSession.project, MemoryEntry.chat_session, and PromptUsageTemplate.prompt.

Improves reverse queries, e.g. assistant.chat_sessions.all().

Consolidate embedding models or add cross-link

Link EmbeddingMetadata to embeddings.Embedding or add a ForeignKey from EmbeddingMetadata back to its DocumentChunk in a consistent manner.

Ensures all vectors can be traced to their originating chunk or memory.

Auto-assign memory_context on ingest

In the ingestion endpoint, default Document.memory_context to the assistant’s context when assistant_id is provided to avoid orphan documents.

Add indexes on frequent queries

Index MemoryEntry.assistant, MemoryEntry.context, and AssistantChatMessage.session for faster lookups.

Validation command for embedding links

Extend repair_rag_chunk_links or create a new management command to validate Embedding.content_id against existing objects and report mismatches.

This overview maps how documents, memories, embeddings, and prompts connect throughout the system. Adding the recommended fixes will strengthen reverse access patterns and prevent future linkage errors.
