# 🧠 Phase Ω.7.21.b — Anchor Boost Tuning + Weak Match Recovery

## 🎯 Objective
Improve assistant RAG relevance and recovery when glossary anchors are matched but chunks fall below strict similarity thresholds.

---

## 🛠️ Goals

### ⚙️ 1. Glossary-Driven Boosting
- Slightly **boost chunk similarity scores** for chunks that contain glossary matches
- Helps low-similarity but glossary-rich chunks rise to top-3 retrieval

### 🛡️ 2. Anchor Match Override
- **Guarantee at least one chunk with a matching glossary anchor** is returned
- Even if its vector similarity is low, its glossary match justifies inclusion

### 💡 3. UI Clarity
- Add a **"Glossary Anchor Override"** badge to debug panel
- Tag chunks that were included due to anchor match rather than vector score alone

---

## 🔍 Example Debug Use Case

| Query | Glossary Anchor | Base Score | Action |
|-------|------------------|------------|--------|
| “What is the EVM?” | `ethereum-virtual-machine` | 0.32 | Force include |
| “Secure Solidity contracts” | `smart-contract` | 0.67 | Boost slightly |
| “zk-rollup gas” | `zk-rollup` | 0.91 | Normal match |

---

## 🚀 Dev Tasks

### 🔹 Backend
- [ ] Patch chunk retrieval to add `glossary_boost_factor` (e.g., `+0.1 to +0.2`)
- [ ] Implement fallback override: always include at least one glossary-matching chunk if present
- [ ] Mark chunks in debug output with `override_reason: "anchor-match"`

### 🔹 Frontend
- [ ] Show "Glossary Anchor Override" badge next to any forced-included chunks
- [ ] Tooltip: “This chunk was included due to a glossary match even though its vector score was low.”

---

## 🧪 Test Queries After Patch
- [ ] “What is the Ethereum Virtual Machine?”
- [ ] “How do smart contracts store data?”
- [ ] “Why are zk-rollups gas efficient?”

---

## 🔁 Linked Context
- Previous Phase: Ω.7.21 — Chunk Glossary Match Scoring + RAG Recall Debug
- Assistant: `solidity-dev-assistant`
- Glossary Anchors: `smart-contract`, `zk-rollup`, `ethereum-virtual-machine`