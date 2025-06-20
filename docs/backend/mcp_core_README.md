# 🧠 MCP Core — Model Context Protocol Layer

Welcome to `mcp_core/` — the central coordination layer that acts as the **protocol interface** between your AI models (e.g. assistants, agents) and external tools, data sources, and memory.

---

## 📦 Purpose

The `mcp_core` app is **not** where you define or run agents. Instead, this is where you build and manage the logic that connects your assistant or agent layer to:

- Filesystems and local data tools
- Memory and reflection workflows
- Model-agnostic context routing
- Prompt logging and diagnostic utilities
- Agent feedback and tagging pipelines

---

## 🧩 Module Overview

| File                         | Purpose                                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------------------- |
| `agent_controller.py`        | Central utility for running agents, routing messages, and managing output consistency    |
| `agent_reflection_engine.py` | Reflection and self-evaluation system for agent thought logs and performance             |
| `auto_tag_from_embedding.py` | Auto-tags memory entries and logs based on vector similarity                             |
| `debugger_agent.py`          | Special-purpose agent that runs diagnostics on prompt errors, agent output, and failures |
| `log_prompt.py`              | Logs prompts, system inputs, and outputs for debugging, analytics, and version control   |
| `tagging.py`                 | Manual and AI-driven tagging logic for agents, memories, and threads                     |
| `thread_helpers.py`          | Thread + conversation linkage utilities for creating narrative memory structures         |

---

## 🧪 MCP Integration Plan

In future iterations, this app will act as the interface for **MCP Servers**, including:

- Filesystem access for local documents
- API execution (GitHub, Notion, Jira, etc.)
- Standardized context routing to sub-agents or toolkits

Each external system will expose an MCP-compatible endpoint, and `mcp_core` will act as the bridge from assistant context → external system → structured result.

---

## 🔁 Related Apps

| App           | Role                                               |
| ------------- | -------------------------------------------------- |
| `agents/`     | Agent profiles, UIs, execution styles              |
| `assistants/` | Long-term assistant behavior, memory, thought logs |
| `intel_core/` | Ingestion, chunking, embeddings                    |
| `memory/`     | Memory entries, feedback, threading, conversations |

---

## 📍Directory Placement

Drop this `README.md` into:

```bash
docs/mcp_core_README.md
```

---

## 🚀 Bootstrap Example: DevOps Assistant

Running `python manage.py seed_dev_assistant` performs a quick assistant →
project setup:

1. Creates the **Zeno the Build Wizard** assistant.
2. Generates a `Project` linked back to that assistant.
3. Attaches all `DevDoc` entries as project context.
4. Logs a summary reflection via `AssistantThoughtLog`.

This command lives in
`mcp_core/management/commands/seed_dev_assistant.py` and can be used as a
template for future bootstrap scripts.
