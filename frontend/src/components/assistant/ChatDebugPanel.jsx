import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ChatDebugPanel({ ragMeta, slug }) {
  if (!ragMeta) return null;
  const [showAll, setShowAll] = useState(false);
  const used = ragMeta.used_chunks || [];
  const candidates = ragMeta.candidates || [];
  const score = ragMeta.retrieval_score ?? 0;
  const list = showAll ? candidates : used;
  const showTip = score < 0.2 && used.length === 0;
  const glossaryMissing = ragMeta.glossary_present === false;
  const showSuggest =
    glossaryMissing || score === 0 || (ragMeta.glossary_chunk_ids || []).length === 0;

  if (ragMeta.chunks_searched === 0) {
    console.warn(
      "RAG scope issue: zero chunks searched for",
      ragMeta.memory_context_id
    );
  }

  async function suggestAnchor() {
    const term = ragMeta.query || ragMeta.query_text || "";
    if (!term) return;
    try {
      const url = slug
        ? `/assistants/${slug}/suggest_glossary_anchor/`
        : "/intel/glossary/suggest/anchor/";
      await apiFetch(url, {
        method: "POST",
        body: { term },
      });
      alert("Suggestion submitted");
    } catch (err) {
      console.error("Suggest failed", err);
    }
  }

  return (
    <div className="border rounded p-2 mt-3">
      <h6>Chat Debug</h6>
      <div className="small mb-1">
        Context: {ragMeta.memory_context_id || "global"}
        {ragMeta.chunks_searched !== undefined && (
          <> — Chunks searched: {ragMeta.chunks_searched}</>
        )}
      </div>
      {showTip && (
        <div className="alert alert-warning small">
          🧠 Tip: The document may be noisy, too short, or semantically distant. Consider re-embedding or increasing similarity tolerance.
        </div>
      )}
      {ragMeta.fallback_reason && (
        <div className="small text-danger mb-1">Fallback Reason: {ragMeta.fallback_reason}</div>
      )}
      {candidates.length > 0 && (
        <div className="form-check form-switch mb-2">
          <input
            className="form-check-input"
            type="checkbox"
            id="showAllChunksToggle"
            checked={showAll}
            onChange={() => setShowAll(!showAll)}
          />
          <label className="form-check-label" htmlFor="showAllChunksToggle">
            Show all retrieved chunks (incl. low scores)
          </label>
        </div>
      )}
      {showSuggest && (
        <button
          className="btn btn-sm btn-outline-secondary mb-2"
          onClick={suggestAnchor}
        >
          Suggest Glossary Anchor
        </button>
      )}
      {ragMeta.glossary_expected && ragMeta.glossary_present === false && (
        <div className="alert alert-warning small mb-1">
          Glossary expected but no glossary chunks found.
        </div>
      )}
      {list.length > 0 ? (
        <ul className="small mb-0">
          {list.map((c) => (
            <li key={c.chunk_id || c.id}>
              <code>{(c.score ?? c.final_score)?.toFixed(3)}</code> { (c.text || c.content || "").slice(0, 60) }
            </li>
          ))}
        </ul>
      ) : (
        <div className="small text-muted">No chunks used.</div>
      )}
    </div>
  );
}
