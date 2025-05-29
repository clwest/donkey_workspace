import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function reasonClass(reason) {
  if (!reason) return "bg-secondary";
  if (reason.includes("missing")) return "bg-danger";
  if (reason.includes("filtered")) return "bg-warning text-dark";
  return "bg-secondary";
}

export default function RagFailureTable() {
  const [entries, setEntries] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/static/rag_failures.json")
      .then((res) => res.json())
      .then((data) => setEntries(Array.isArray(data) ? data : []))
      .catch(() => setEntries([]));
  }, []);

  if (entries.length === 0) {
    return (
      <div className="container my-4">
        <h3>RAG Failure Log</h3>
        <div className="text-muted">No failures logged.</div>
      </div>
    );
  }

  return (
    <div className="container my-4">
      <h3>RAG Failure Log</h3>
      <table className="table table-bordered table-sm">
        <thead className="table-light">
          <tr>
            <th>Query</th>
            <th>Assistant</th>
            <th>Anchor(s)</th>
            <th>Used Chunks</th>
            <th>Expected Chunks</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr
              key={e.id}
              style={{ cursor: "pointer" }}
              onClick={() => navigate(`/debug/rag-replay/${e.id}`)}
            >
              <td className="text-truncate" style={{ maxWidth: 200 }}>{e.query}</td>
              <td>{e.assistant}</td>
              <td>
                {(e.anchors || []).map((a) => (
                  <span key={a} className="badge bg-primary me-1">
                    {a}
                  </span>
                ))}
              </td>
              <td className="text-muted small">
                {(e.used_chunks || []).join(", ") || "—"}
              </td>
              <td className="text-muted small">
                {(e.expected_chunks || []).join(", ") || "—"}
              </td>
              <td>
                <span className={"badge " + reasonClass(e.reason)}>
                  {e.reason || "unknown"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
