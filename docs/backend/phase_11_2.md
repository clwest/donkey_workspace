# Phase 11.2 — Codex Mutation Editors, Symbolic Style Guides & Interactive Memory Ritual Sandboxes

Phase 11.2 introduces visual editing tools for codices and rituals. Assistants can now experiment with belief mutations, tune their visual identity, and test rituals in a safe sandbox.

## Core Components

### CodexMutationEditor
```jsx
function CodexMutationEditor({ codex }) {
  // interactive editor showing mutation history and belief impact
  return <div>...</div>;
}
```
Shows codex state, mutation log, and preview of symbolic effects. Includes draft mode and ritual validation.

### SymbolicStyleGuidePanel
```jsx
function SymbolicStyleGuidePanel({ assistant }) {
  // live tone and aura guide for an assistant
  return <aside>...</aside>;
}
```
Displays tone profile, codex aura color, and alignment percent to keep assistants visually consistent.

### MemoryRitualSandbox
```jsx
function MemoryRitualSandbox({ blueprint, memories }) {
  // drag/drop memories and preview ritual outcome
  return <section>...</section>;
}
```
Allows experimentation with ritual overlays and belief scoring before committing changes.

## View Routes
- `/codex/edit`
- `/assistants/:id/style`
- `/rituals/sandbox`

## Testing Goals
- Codex mutations preserve history and show impact previews
- Style panel reflects codex tone and alignment
- Sandbox rituals log outputs and memory shifts
