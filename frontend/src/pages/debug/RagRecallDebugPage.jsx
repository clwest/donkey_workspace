import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RagRecallDebugPage() {
  const [query, setQuery] = useState("");
  const [assistant, setAssistant] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const runQuery = async () => {
    setError(null);
    try {
      const res = await apiFetch("/intel/debug/rag-recall/", {
        params: { query, assistant },
      });
      setData(res);
    } catch (err) {
      console.error("Failed to fetch recall", err);
      setError("Failed to load recall data");
    }
  };

  const candidates = data?.debug?.candidates || [];

  return (
    <div className="container my-4">
      <h3>RAG Recall Debug</h3>
      <div className="mb-3">
        <input
          className="form-control mb-2"
          placeholder="Query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <input
          className="form-control mb-2"
          placeholder="Assistant ID or slug"
          value={assistant}
          onChange={(e) => setAssistant(e.target.value)}
        />
        <button className="btn btn-primary" onClick={runQuery}>
          Run
        </button>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      {data && (
        <div>
          <h5>Candidate Chunks</h5>
          <table className="table table-bordered table-sm">
            <thead className="table-light">
              <tr>
                <th>ID</th>
                <th>Score</th>
                <th>Anchor</th>
                <th>Forced</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr
                  key={c.id}
                  className={c.was_filtered_out ? "table-warning" : ""}
                >
                  <td>
                    <code>{c.id}</code>
                  </td>
                  <td>{c.final_score?.toFixed(3)}</td>
                  <td>{c.was_anchor_match ? "🔗" : ""}</td>
                  <td>{c.forced_included ? "✅" : ""}</td>
                  <td>
                    {c.override_reason || c.excluded_reason || ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
