import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RagDebugPanel({ slug }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fallbackOnly, setFallbackOnly] = useState(false);
  const [lowScoreOnly, setLowScoreOnly] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const params = {};
      if (fallbackOnly) params.fallback = "true";
      if (lowScoreOnly) params.score_lt = 0.4;
      const res = await apiFetch(`/assistants/${slug}/rag_debug/`, { params });
      setLogs(res.results || []);
    } catch (err) {
      console.error("Failed to load logs", err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [slug, fallbackOnly, lowScoreOnly]);

  const boostTerms = async (terms) => {
    try {
      await apiFetch(`/assistants/${slug}/boost_anchors/`, {
        method: "POST",
        body: { terms },
      });

      const termList = Array.isArray(terms) ? terms.join(", ") : terms;
      alert(`Boosted ${termList}`);
      load();

    } catch {
      alert("Boost failed");
    }
  };

  return (
    <div>
      <div className="d-flex gap-3 mb-2">
        <div className="form-check">
          <input
            className="form-check-input"
            type="checkbox"
            id="fallbackToggle"
            checked={fallbackOnly}
            onChange={() => setFallbackOnly(!fallbackOnly)}
          />
          <label className="form-check-label" htmlFor="fallbackToggle">
            Fallback Only
          </label>
        </div>
        <div className="form-check">
          <input
            className="form-check-input"
            type="checkbox"
            id="scoreToggle"
            checked={lowScoreOnly}
            onChange={() => setLowScoreOnly(!lowScoreOnly)}
          />
          <label className="form-check-label" htmlFor="scoreToggle">
            Score &lt; 0.4
          </label>
        </div>
        <button
          className="btn btn-sm btn-outline-primary"
          onClick={load}
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>
      <table className="table table-bordered table-sm">
        <thead className="table-light">
          <tr>
            <th>Query</th>
            <th>Score</th>
            <th>Used Chunks</th>
            <th>Glossary Hits</th>
            <th>Glossary Misses</th>
            <th>Fallback</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <React.Fragment key={log.id}>
              <tr>
                <td className="text-break" style={{ maxWidth: 200 }}>{log.query}</td>
                <td>{log.retrieval_score?.toFixed(2)}</td>
                <td className="small text-muted">
                  {(log.used_chunk_ids || []).join(", ") || "—"}
                </td>
                <td className="small">{(log.glossary_hits || []).join(", ")}</td>
                <td className="small">{(log.glossary_misses || []).join(", ")}</td>
                <td>{log.fallback_triggered ? "⚠️" : ""}</td>
                <td className="small text-danger">{log.fallback_reason || ""}</td>
              </tr>
              {log.glossary_misses?.length > 0 && (
                <tr>
                  <td colSpan="7">
                    <button
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => boostTerms(log.glossary_misses)}
                    >
                      Boost Glossary Terms
                    </button>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
