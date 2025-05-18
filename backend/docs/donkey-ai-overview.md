Below is a high-level, cross-cutting view of the entire Donkey-AI-Assistants Django project—its major apps, how they already tie together, and the places where we still need
to wire things up.

        1. Overall Architecture
           •  The project is composed of a set of loosely coupled “feature” apps plus a core user/Auth layer.
           •  Apps communicate primarily via Django ForeignKeys or M2M’s (and in a few cases by storing UUIDs or free-text IDs).
           •  There is also a suite of “service” / “helper” modules—embeddings, trainers, prompt-generation, vector ops, etc.—that backfill each feature area.
        2. App Roles and Responsibilities
           •  accounts: your custom User model (via settings.AUTH_USER_MODEL).
           •  agents: (mostly empty) placeholder for “agent” definitions.
           •  assistants: conversational AI “assistant” definitions, chat sessions, thought/reflection logs, objectives & tasks, prompt links, metrics, etc.
           •  characters: character profiles, reference images, training profiles.
           •  embeddings: generic vector store + story-chunk embeddings + semantic tags.
           •  images: image-generation requests (initial, inpaint, upscale, edit), styles (PromptHelper), galleries (ProjectImage), logs.
           •  memory: low-level memory entries, memory chains, memory-centric reflection logs, feedback.
           •  mcp_core: higher-level memory context + plan/task/agent domain model + reflection/action logs + prompt usage logs.
           •  prompts: CRUD for Prompt templates, tags, per-user preferences, and triggerable PromptUsageTemplates.
           •  project: simple “Project” container (title, slug, collaborators, themes).
           •  story: story generation, text + summary + media attachments (image, cover, TTS), themes/tags, reward flags.
           •  trainers: registry of external ML models (ReplicateModel) + their prediction jobs (ReplicatePrediction).
           •  tts: text-to-speech jobs for stories (StoryAudio) and scene images (SceneAudio).
           •  videos: video-generation requests tied to projects/stories/paragraphs; metadata + external job tracking.
        3. What’s Already Connected
           •  **accounts → everyone**: nearly every model FK’s to User for ownership/audit.
           •  **assistants ↔ memory**: thoughts and projects are seeded from MemoryEntry; ChatSession links to assistant and generates StructuredMemory,
    TokenUsage, AssistantChatMessage, etc.
           •  **assistants ↔ prompts**: system_prompt FK; AssistantPromptLink, AssistantMemoryChain and PromptUsageTemplate (in prompts) drive automation.
           •  **project ↔ images/story/tts/videos/characters**: Project FK is used everywhere for user content grouping.
           •  **story ↔ images**: Story holds a FK to images.Image; StoryChunkEmbedding (in embeddings) also ties back to Story.
           •  **story ↔ tts**: OneToOne StoryAudio used for TTS of story text.
           •  **story ↔ characters**: via `character` FK and `characters` M2M.
           •  **images ↔ characters**: CharacterProfile ↔ image reference and styles (PromptHelper).
           •  **prompts ↔ assistants**: PromptUsageTemplate.agent binds prompts to assistants.
           •  **trainers ↔ user**: predictions are owned by user; models registry exists.
        4. Gaps & Missing Integrations


            1. **mcp_core**
                     – No linkage to `project.Project`, `story.Story`, `images.Image` or TTS/Video.
                     – PromptUsageLog stores only slugs/UUIDs; could FK to `prompts.Prompt` and `PromptUsageTemplate`.
                     – MemoryContext is free-text; could GenericForeignKey to any “target” model (Agent, Task, Plan, Project).

            2. **memory**
                     – `MemoryEntry.related_project` is a CharField—should FK to `project.Project`.
                     – MemoryChain has no ordering index.
                     – ReflectionLog/MemoryFeedback exist both here and in mcp_core (duplication of “reflection”).
                     – Tags are ArrayFields; consider a central `Tag` model.

            3. **embeddings**
                     – Generic Embedding.content_type/content_id is free-text. A proper `ContentType`/GenericForeignKey would enforce integrity.
                     – Only story chunks get a first-class model; other domains (memory entries, assistant thoughts, chat messages) could have specialized
    embedding tables.

            4. **prompts**
                     – PromptUsageTemplate covers triggers for assistants, but other domains (story generation, image/video jobs, TTS) often build prompts
    ad-hoc. Could unify under PromptUsageTemplate + usage logs.
                     – Per-user `PromptPreferences` is narrow (trimming, excluded sections); could include defaults for tone, complexity, fallback strategies.

            5. **trainers**
                     – ReplicatePrediction.files holds URLs but is never FK’d into Image, Video, or TTS models. Jobs that produce images/videos should create
    `images.Image` or `videos.Video` instances on success.

            6. **videos & tts**
                     – Both use free-text `theme` and ArrayField `tags`. Should M2M to a `ThemeHelper` or `Tag` model (e.g. reuse `images.TagImage` or
    `prompts.PromptTag`).
                     – No common abstract base/mixin for status/provider fields.

            7. **project vs. Project**
                     – Two “project” concepts live side-by-side: the simple user‐owned `project.Project` and the assistants’ `Project`. These should
    be reconciled or mapped.

            8. **characters**
                     – CharacterTrainingProfile embedding is JSON; could be a VectorField in `embeddings`.
                     – Many styles/prompts are duplicated between PromptHelper (images) and Prompt (prompts). Consider unifying naming.
        5. Next Steps
           •  Adopt Django’s ContentType/GenericForeignKey where you need polymorphic links (embeddings, mcp_core.MemoryContext).
           •  Replace free-text FKs (`related_project`, `theme`, `project` in memory) with real ForeignKeys to `project.Project`.
           •  Consolidate tagging under a single `Tag` model (or multi-app M2M pattern).
           •  Wire your trainers’ predictions back into your media models (Image, Video, StoryAudio) via on-success callbacks.
           •  Merge the two “project” concepts (Project vs. Project) or clearly demarcate their domains.
           •  Abstract common status/provider/job-tracking fields in TTS/Video/Images/Trainers into shared mixins.
           •  Ensure prompt usage logs all domains—image, video, TTS, story—via a unified PromptUsageLog that FK’s to Prompt, Assistant, Project, etc.

    —
    With these connections in place, you’ll have a fully integrated ecosystem: assistants driving memory and planning, prompts managed centrally, media
    (images/video/tts) linked into stories/projects, all searchable and vectorized via embeddings, and usage audited end-to-end.
