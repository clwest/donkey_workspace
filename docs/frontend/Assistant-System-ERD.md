# 🧠 Assistant System — Entity Relationship Diagram (ERD)

---

```plaintext
🔼 AssistantProject
├── id (UUID)
├── slug (Slug)
├── title (CharField)
├── description (TextField)
├── status (CharField)
├── created_from_memory (FK)
├── created_at (DateTime)
```

### AssistantProject has many:

```plaintext
├── ProjectTask
├── ProjectMilestone
├── AssistantObjective
├── AssistantReflection
├── AssistantMemoryChain
│   └── AssistantMemoryChainLink (links to MemoryEntry)
├── ProjectMemoryLink (direct links to MemoryEntry)
```

---

### ProjectTask

```plaintext
├── id (UUID)
├── project (FK)
├── title (CharField)
├── notes (TextField)
├── content (TextField)
├── status (CharField)
├── priority (IntegerField)
├── created_at (DateTime)
```

### ProjectMilestone

```plaintext
├── id (UUID)
├── project (FK)
├── title (CharField)
├── description (TextField)
├── due_date (DateField)
├── completed (Boolean)
├── status (CharField)
├── created_at (DateTime)
```

### AssistantObjective

```plaintext
├── id (UUID)
├── project (FK)
├── title (CharField)
├── description (TextField)
├── is_completed (Boolean)
├── created_at (DateTime)
```

### AssistantReflection

```plaintext
├── id (UUID)
├── project (FK)
├── title (CharField)
├── content (TextField)
├── mood (CharField)
├── created_at (DateTime)
```

### AssistantMemoryChain

```plaintext
├── id (UUID)
├── project (FK to AssistantProject)
├── title (CharField)
├── created_at (DateTime)
```

### AssistantMemoryChainLink

```plaintext
├── id (UUID)
├── memory_chain (FK)
├── memory (FK to MemoryEntry)
├── notes (TextField)
├── created_at (DateTime)
```

---

## 🚼 Notes:

- All major models are tied back to `AssistantProject`.
- `MemoryEntry` links are bridged by `ProjectMemoryLink` and `AssistantMemoryChainLink`.
- Reflections, Next Actions, Chains, and Objectives are all per-project.

---

## 📺 Visual Relationship Map:

```plaintext
AssistantProject
├── ProjectTask
├── ProjectMilestone
├── AssistantObjective
├── AssistantReflection
├── AssistantMemoryChain
│    └── AssistantMemoryChainLink (links to MemoryEntry)
└── ProjectMemoryLink (direct links to MemoryEntry)
```

---

## 📚 This document generated: April 28, 2025
