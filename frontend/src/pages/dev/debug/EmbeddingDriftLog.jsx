import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function EmbeddingDriftLog() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/dev/embedding-drift-log/");
        setRows(res.logs || []);
      } catch (err) {
        setError(err);
      }
    }
    load();
  }, []);

  if (error) return <div className="container py-3">Failed to load log.</div>;
  if (!rows) return <div className="container py-3">Loading...</div>;

  return (
    <div className="container py-3">
      <h3>Embedding Drift Log</h3>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Model</th>
            <th>Mismatched</th>
            <th>Orphans</th>
            <th>Repaired</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              <td>{row.timestamp.slice(0, 19)}</td>
              <td>{row.model_name}</td>
              <td>{row.mismatched_count}</td>
              <td>{row.orphaned_count}</td>
              <td>{row.repaired_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
