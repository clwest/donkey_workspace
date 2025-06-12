import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function EmbeddingDebug() {
  const [data, setData] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/dev/embedding-debug/");
        setData(res);
      } catch (err) {
        console.error("Failed to load embedding stats", err);
      }
    }
    load();
  }, []);

  if (!data) {
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
    </div>
  );
}
