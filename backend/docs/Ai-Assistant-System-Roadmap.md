# 🧠 AI Assistant System Roadmap

> This roadmap captures the current structure and suggests logical next steps across key areas of the assistant project. It’s designed for modular progress and AI pair-building.

---

## ✅ Current Functional Areas

### 📂 `prompts/`

- System prompt ingestion from markdown
- Metadata extraction (type, source, tags)
- Prompt remixing (with embedded output)
- Embedded via OpenAI + PGVector
- Searchable by similarity

### 📂 `assistants/`

- Project-scoped assistant thoughts + reflections
- Auto-thought + auto-reflection thresholding
- Project summaries
- Embeddings for thoughts and reflections

### 📂 `memory/`

- MemoryEntry + ReflectionLog
- Memory chains
- Optional voice clip support
- Tied into assistant reflections and prompt generation

### 📂 `mcp_core/`

- Core planning and task models (Plan, Task, Agent)
- Reflection logs with related memories
- MemoryContext for structured storage and search

### 📂 `embeddings/`

- Embedding helpers + retry/backoff
- Smart chunking and fingerprinting
- PGVector-backed similarity search
- Session caching with Redis
- Generalized search API endpoints

---

## 🔮 Suggested Next Features

### �� Prompt Explorer Polish

- [ ] Search bar: text + vector similarity
- [ ] Filter by tag / type / source
- [ ] Markdown-style rendering of content
- [ ] Highlight token count, tone, complexity

### 🧠 Assistant Memory Tools

- [ ] Save any prompt/memory to Assistant Memory
- [ ] “Reflect on this prompt” → stores summary
- [ ] Track prompt usage per project
- [ ] Timeline or graph of memory chains

### 🔍 Cross-Project Search UI

- [ ] Search all prompts, thoughts, or memories
- [ ] Display sorted results with score
- [ ] Filter by type/source/importance
- [ ] Result preview + “jump to detail”

### 🤖 Assistant Agent Loader

- [ ] Assign prompts to agents
- [ ] Load system prompt as personality
- [ ] Run prompt-based test sessions (chat window)
- [ ] Plan/Task coordination with memory context

### 🧪 Prompt Testing Playground

- [ ] Pick original + remixed prompt
- [ ] Input test user message
- [ ] Preview GPT response from both
- [ ] Compare side-by-side: tone, style, clarity

---

## 🔧 Maintenance / Backend Enhancements

- [ ] `reembed_all_prompts` command
- [ ] Auto-embed after remix/save
- [ ] Admin import/export of prompt sets
- [ ] Add more model targets to search registry
