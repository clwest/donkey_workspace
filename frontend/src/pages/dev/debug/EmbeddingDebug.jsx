import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import ErrorCard from "../../../components/ErrorCard";

export default function EmbeddingDebug() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [showRag, setShowRag] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const url = showRag ? "/dev/embedding-debug/?include_rag=1" : "/dev/embedding-debug/";
        const res = await apiFetch(url);
        setData(res);
      } catch (err) {
        console.error("Failed to load embedding stats", err);
        setError(err);
      }
    }
    load();
  }, [showRag]);

  if (error?.status === 403) {
    return <ErrorCard message="You don't have permission to view embedding diagnostics." />;
  }

  if (!data && !error) {
    return <div className="container py-4">Loading...</div>;
  }

  return (
    <div className="container py-4">
      <h3>Embedding Debug</h3>
      <h5 className="mt-3">Model Counts</h5>
      <table className="table table-sm w-auto">
        <thead>
          <tr>
            <th>Model</th>
            <th>Count</th>
          </tr>
        </thead>
        <tbody>
          {data.model_counts.map((row) => (
            <tr key={row.model_used || "unknown"}>
              <td>{row.model_used || "Unknown"}</td>
              <td>{row.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-4">
        <strong>Embeddings with invalid links: {data.invalid_links}</strong>
      </div>
      <h5 className="mt-4">By Assistant &amp; Context</h5>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Assistant</th>
            <th>Context ID</th>
            <th>Count</th>
          </tr>
        </thead>
        <tbody>
          {data.assistant_breakdown.map((row, idx) => (
            <tr key={idx}>
              <td>{row.content_object__assistant__slug || row.content_object__assistant__id}</td>
              <td>{row.content_object__context_id}</td>
              <td>{row.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="form-check form-switch mt-4">
        <input
          className="form-check-input"
          type="checkbox"
          id="ragToggle"
          checked={showRag}
          onChange={(e) => setShowRag(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="ragToggle">
          Show Retrieval Stats
        </label>
      </div>
      {showRag && data.context_stats && (
        <div className="mt-3">
          <h5>Context Retrieval Counts</h5>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Assistant</th>
                <th>Context ID</th>
                <th>Chunks</th>
              </tr>
            </thead>
            <tbody>
              {data.context_stats.map((row, idx) => (
                <tr key={idx}>
                  <td>{row.assistant}</td>
                  <td>{row.context_id}</td>
                  <td>{row.chunk_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
