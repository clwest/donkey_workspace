# Assistant Dashboard Overview

This document summarizes the current state of the Assistant Detail interface, diagnostic tooling, reflection pipeline, and RAG debugging UI.

---

## Core Components

### ✅ Assistant Identity Panel

- Slug: `godelbot`
- Tone: friendly
- Planning: short_term
- Linked user: tom
- Status: Active
- Model: gpt-4o

### 📊 Dashboard Stats

- Memory Entries: 1
- Glossary Terms: 0
- Badges: 0
- Reflections: 0
- Drifted Anchors: 0

---

## 🔍 Diagnostics & Debug

### Assistant Diagnostics Panel

- Memory Context: 744
- Glossary Anchors: 37 (3 matched)
- Fallbacks: 0
- Orphaned Memories: 0
- Health: Moderate Match

> Pie chart visual: Score distribution (High, Medium, Low)

### RAG Debug Tools

- RAG Grounding Inspector
- Glossary Drift Report
- Drift Heatmap
- Anchor Health Panel
- RAG Diagnostics Runner
- Reflection Group Viewer

---

## 🛠 Tools and Project Binding

- Linked Document support
- Memory filtering + reflection
- Tool assignment and training
- Diagnostic console
- CLI runner and recovery panel

---

## Recovery Panel

- Recovery Status: `57 / 175`
- Buttons:
  - Run Recovery
  - Reflect Again
  - Repair Documents

---

## 🔁 Reflection Support

- First question summary
- Thought logs
- Session view
- Boot diagnostics
- Memory cleanup tools

---

## ✅ Suggested Followups

- Export full assistant detail snapshot (PDF or markdown)
- Link assistant reflections and RAG score logs
- Add CLI task for `generate_dashboard_summary --assistant godelbot`

---
