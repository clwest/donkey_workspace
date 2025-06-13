import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function EmbeddingAuditPanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/dev/embedding-audit/");
        setData(res);
      } catch (err) {
        setError(err);
      }
    }
    load();
  }, []);

  if (error) {
    return <div className="container py-3">Failed to load audit data.</div>;
  }

  if (!data) {
    return <div className="container py-3">Loading...</div>;
  }

  return (
    <div className="container py-3">
      <h3>Embedding Audit</h3>
      <table className="table table-sm mt-3 w-auto">
        <thead>
          <tr>
            <th>Model</th>
            <th>Mismatched</th>
            <th>Orphans</th>
          </tr>
        </thead>
        <tbody>
          {data.results.map(([model, row]) => (
            <tr key={model}>
              <td>{model}</td>
              <td>{row.mismatched}</td>
              <td>{row.orphans}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.recent_orphans && data.recent_orphans.length > 0 && (
        <details className="mt-3">
          <summary>Recent Orphans</summary>
          <pre className="mt-2 bg-light p-2">
            {data.recent_orphans
              .map((o) => `${o.embedding_id} - ${o.reason}`)
              .join("\n")}
          </pre>
        </details>
      )}
    </div>
  );
}

