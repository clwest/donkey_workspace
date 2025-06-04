import { useState } from "react";

export default function ChatDebugPanel({ ragMeta }) {
  if (!ragMeta) return null;
  const [showAll, setShowAll] = useState(false);
  const used = ragMeta.used_chunks || [];
  const candidates = ragMeta.candidates || [];
  const score = ragMeta.retrieval_score ?? 0;
  const list = showAll ? candidates : used;
  const showTip = score < 0.2 && used.length === 0;
  const glossaryMissing = ragMeta.glossary_present === false;

  return (
    <div className="border rounded p-2 mt-3">
      <h6>Chat Debug</h6>
      {showTip && (
        <div className="alert alert-warning small">
          🧠 Tip: The document may be noisy, too short, or semantically distant. Consider re-embedding or increasing similarity tolerance.
        </div>
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
      {glossaryMissing && (
        <button className="btn btn-sm btn-outline-secondary mb-2">
          Suggest Glossary Anchor
        </button>
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
