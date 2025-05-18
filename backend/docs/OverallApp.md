Here's a visual breakdown of the system architecture including the assistants, embeddings, memory, and mcp_core apps. Now we'll add in the two remaining critical pieces: `prompts` and `images`.

---

**✅ Current High-Level Architecture:**

```
+------------------+      +---------------------+      +----------------+      +------------------+
|   Assistants     |<---->|     MCP Core        |<---->|   Embeddings   |<---->|     Memory        |
| (Thoughts, CoT)  |      | (Agents, Logs,      |      | (Chunking,     |      | (Memories,       |
| Projects, Tasks) |      |  Reflection Engine) |      |  Search, Tags) |      |  Feedback, Chains)|
+------------------+      +---------------------+      +----------------+      +------------------+
       |                                                      ^
       |                                                      |
       v                                                      |
+------------------+                                          |
|    Prompts       |<------------------------------------------+
|  (Prompt sets,   |
|   versioning,    |
|   mutation, tags)|
+------------------+
       ^
       |
       v
+------------------+
|     Images       |
| (Prompt Styles,  |
|  ThemeHelpers,   |
|  Story Images)   |
+------------------+
```

---

**🧠 Assistants**

- Thought logging, project planning, CoT tracing
- Supports long-term memory and chain-of-thought reflection

**📚 MCP Core**

- Hosts agent reasoning, planning, reflection, and prompt usage logs

**🧩 Embeddings**

- Chunked vector search, tagging, Redis-backed caching, smart processing

**🧠 Memory**

- Stores user or assistant memory, links thoughts and projects, supports feedback

**🪄 Prompts**

- Core prompt management system (manual, mutated, embedded, versioned)
- Includes tag inference, prompt mutation types, diagnostics

**🎨 Images**

- Structured visual prompt templates (PromptHelpers)
- Theme discovery and remixing (ThemeHelpers)
- Supports image generation for characters, scenes, and storybook content

---

Let me know what you want to do next: visually show data flow, highlight all Redis/embedding usage, or focus on one of the feature pipelines (e.g. prompt creation → embedding → tagging → mutation).
