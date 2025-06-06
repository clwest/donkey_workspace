import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function RagGroundingInspectorPage() {
  const { slug } = useParams();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/assistants/${slug}/rag_debug/`);
      setLogs(res.results || []);
    } catch (err) {
      console.error("Failed to load grounding logs", err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [slug]);

  const boost = async (term) => {
    try {
      await apiFetch(`/glossary/boost_anchor/`, {
        method: "POST",
        body: { anchor: term, boost: 0.1 },
      });
      alert(`Boosted ${term}`);
    } catch {
      alert("Boost failed");
    }
  };

  return (
    <div className="container my-5">
      <h2 className="mb-3">RAG Grounding Inspector</h2>
      <div className="d-flex justify-content-end mb-2">
        <Link
          to={`/anchor/mutations?assistant=${slug}`}
          className="btn btn-sm btn-outline-primary"
        >
          🧪 Review Mutation Suggestions
        </Link>
      </div>
      <button className="btn btn-outline-primary mb-3" onClick={loadLogs} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh"}
      </button>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Query</th>
            <th>Chunks</th>
            <th>Score</th>
            <th>Fallback</th>
            <th>Glossary Misses</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td className="text-break" style={{ maxWidth: 200 }}>{log.query}</td>
              <td className="small text-muted">
                {(log.used_chunk_ids || []).join(", ") || "—"}
              </td>
              <td>{log.retrieval_score?.toFixed(2)}</td>
              <td>{log.fallback_triggered ? "⚠️" : ""}</td>
              <td>
                {(log.glossary_misses || []).map((m) => (
                  <span key={m} className="me-1">
                    {m}{" "}
                    <button
                      className="btn btn-sm btn-link p-0"
                      onClick={() => boost(m)}
                    >
                      Boost
                    </button>
                  </span>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

