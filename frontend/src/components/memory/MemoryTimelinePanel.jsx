import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import MemoryFeedbackModal from "./MemoryFeedbackModal";

export default function MemoryTimelinePanel({
  assistantId,
  documentId,
  highlightId,
  initialEntries,
}) {
  const [entries, setEntries] = useState(initialEntries || []);
  const [hideWeak, setHideWeak] = useState(false);
  const [feedbackCounts, setFeedbackCounts] = useState({});
  const [activeFeedbackId, setActiveFeedbackId] = useState(null);

  const isWeak = (m) => {
    const imp = m.importance;
    const tokens = m.token_count ?? 999;
    return (imp === "low" || imp <= 2) && tokens < 5;
  };

  useEffect(() => {
    if (initialEntries) return;
    if (!assistantId || !documentId) return;
    async function load() {
      try {
        const res = await apiFetch("/memory/list/", {
          params: {
            assistant_slug: assistantId,
            document_id: documentId,
          },
        });
        setEntries(res);
      } catch (err) {
        console.error("Failed to load memories", err);
        setEntries([]);
      }
    }
    load();
  }, [assistantId, documentId, initialEntries, highlightId]);

  useEffect(() => {
    async function loadCounts() {
      const counts = {};
      await Promise.all(
        (entries || []).map(async (e) => {
          try {
            const res = await apiFetch(`/memory/${e.id}/feedback/`);
            counts[e.id] = Array.isArray(res)
              ? res.filter((f) => !f.resolved && !f.resolved_at).length
              : 0;
          } catch {
            counts[e.id] = 0;
          }
        })
      );
      setFeedbackCounts(counts);
    }
    if (entries.length > 0) {
      loadCounts();
    }
  }, [entries]);

  const shown = hideWeak ? entries.filter((e) => !isWeak(e)) : entries;

  return (
    <div className="mt-4">
      <h5>Memory Timeline</h5>
      <div className="form-check form-switch mb-2">
        <input
          className="form-check-input"
          type="checkbox"
          id="hideWeakToggle"
          checked={hideWeak}
          onChange={(e) => setHideWeak(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="hideWeakToggle">
          Hide Weak Memories
        </label>
      </div>
      <ul className="list-group">
        {shown.map((m) => (
          <li
            key={m.id}
            className={`list-group-item${
              highlightId === m.id ? " list-group-item-success" : ""
            } ${isWeak(m) ? "text-muted" : ""}`}
          >
            <div className="d-flex justify-content-between align-items-start">
              <div className="fw-bold">
                {new Date(m.created_at).toLocaleString()}
                {isWeak(m) && <span className="ms-1">🗑</span>}
              </div>
              <div>
                {feedbackCounts[m.id] > 0 && (
                  <span className="badge bg-danger me-2">
                    {feedbackCounts[m.id]}
                  </span>
                )}
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => setActiveFeedbackId(m.id)}
                >
                  📝
                </button>
              </div>
            </div>
            <div>{m.title || m.summary || m.event}</div>
          </li>
        ))}
        {shown.length === 0 && (
          <li className="list-group-item text-muted">No memories found.</li>
        )}
      </ul>
      {activeFeedbackId && (
        <MemoryFeedbackModal
          memoryId={activeFeedbackId}
          show={!!activeFeedbackId}
          onHide={() => setActiveFeedbackId(null)}
          onSubmitted={() => setActiveFeedbackId(null)}
        />
      )}
    </div>
  );
}
