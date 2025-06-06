# Glossary Fallback Strategy Overview

This document outlines the current strategy for managing glossary term mutations based on fallback frequency in the Donkey Betz assistant system. It serves as a reference guide for making mutation decisions, setting thresholds, and tuning assistant memory reliability.

---

## 🎯 Objective

To improve assistant grounding accuracy by identifying and addressing glossary terms that consistently fail to resolve ("fallbacks") during reflection, RAG, and memory reasoning tasks.

---

## 📊 Fallback Count Guidelines

| Fallback Count | Interpretation                    | Recommendation                 |
| -------------- | --------------------------------- | ------------------------------ |
| 0              | Might be noise or low-priority    | Skip for now                   |
| 1              | Potential instability / edge case | Hold for future review         |
| 2              | Emerging pattern                  | Suggest mutation (user review) |
| **3+**         | Consistent failure                | ✅ Safe to Accept/Auto-Suggest |

---

## ✅ Acceptance Threshold

- Fallback count **>= 3** is the current threshold for confident mutation acceptance.
- These are considered **high-confidence mutation candidates**.

---

## ⏸️ Lower Fallback Handling (0–2)

- **0s and 1s**: Likely noise, hallucination, or transient issues.

  - Should **not** be accepted automatically.
  - Visible in UI, but could be toggled off by default.

- **2s**: Suggested but held for manual review.

  - May be influenced by assistant memory model, context gaps, or reflection quality.

---

## 🧪 Optional UI Filtering

- Mutation review UI should include toggles for:

  - `Show Low-Fallback Terms`
  - `Show Accepted Mutations`
  - `Show Experimental Terms`

- This enables focused review without noise.

---

## 🔁 Convergence Loop (Roadmap)

1. High fallback terms automatically suggested with `suggested_label`
2. Moderate fallback terms queued for user review
3. Low fallback terms optionally reviewed after new data is gathered
4. Mutation **effectiveness** logged: did fallback frequency improve post-acceptance?

---

## 🧠 Assistant Behavior Goal

- Shift assistants toward high-glossary-convergence and low-fallback state
- Prioritize mutation of concepts that repeatedly degrade recall performance
- Balance between accuracy and stability through empirical mutation thresholds

---

## 🔍 Future Enhancements

- Track fallback trends over time per assistant
- Score mutation confidence using embedding similarity
- Backtest mutations on past logs to simulate improvement
- Reinforcement scoring for successful mutation acceptance

---

## Last Reviewed: 2025-06-06

By: Donkey Workspace Intelligence Loop
