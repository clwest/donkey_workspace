import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RagPlaybackPanel({ slug }) {
  const [logs, setLogs] = useState([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    apiFetch(`/assistants/${slug}/rag_debug/`)
      .then((res) => setLogs(res.results || []))
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, [slug]);

  const log = logs[index] || null;

  const next = () => setIndex((i) => Math.min(i + 1, logs.length - 1));
  const prev = () => setIndex((i) => Math.max(i - 1, 0));

  if (loading) return <div>Loading playback...</div>;
  if (!log) return <div className="text-muted">No RAG logs.</div>;

  const rate = (log.retrieval_score || 0).toFixed(2);

  return (
    <div className="mb-3 p-2 border rounded">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <strong>Anchor: {log.expected_anchor || "prompt"}</strong>
        <div>
          <button className="btn btn-sm btn-secondary me-1" onClick={prev} disabled={index === 0}>
            Prev
          </button>
          <button className="btn btn-sm btn-secondary" onClick={next} disabled={index === logs.length - 1}>
            Next
          </button>
        </div>
      </div>
      {log.fallback_triggered && (
        <div className="alert alert-warning py-1">Fallback Triggered: {log.fallback_reason}</div>
      )}
      <div className="small text-muted mb-2">Query: {log.query}</div>
      <ul className="list-group list-group-flush">
        {(log.matched_chunk_ids || log.used_chunk_ids || []).map((cid) => (
          <li key={cid} className="list-group-item">
            <div className="d-flex align-items-center">
              <span className="me-2">{cid}</span>
              <div className="progress flex-grow-1" style={{ height: 6 }}>
                <div
                  className="progress-bar"
                  role="progressbar"
                  style={{ width: `${Math.min(100, (log.retrieval_score || 0) * 100)}%` }}
                />
              </div>
            </div>
          </li>
        ))}
      </ul>
      <div className="mt-2 small">Score: {rate}</div>
    </div>
  );
}

