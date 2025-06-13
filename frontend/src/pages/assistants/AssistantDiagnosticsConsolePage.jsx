import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import useAuthGuard from "../../hooks/useAuthGuard";
import { fetchRagDiagnosticLogs } from "../../api/assistants";
import AssistantDriftPanel from "../../components/embedding/AssistantDriftPanel";

export default function AssistantDiagnosticsConsolePage() {
  useAuthGuard();
  const { slug } = useParams();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("rag");

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetchRagDiagnosticLogs({ assistant: slug });
      setLogs(res.results || []);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (tab === "rag") load();
  }, [slug, tab]);

  return (
    <div className="container my-4">
      <h2 className="mb-3">Diagnostics Console</h2>
      <div className="mb-2">
        <button
          className={`btn btn-sm me-2 ${tab === "rag" ? "btn-primary" : "btn-outline-primary"}`}
          onClick={() => setTab("rag")}
        >
          RAG Logs
        </button>
        <button
          className={`btn btn-sm ${tab === "drift" ? "btn-primary" : "btn-outline-primary"}`}
          onClick={() => setTab("drift")}
        >
          Embedding Drift
        </button>
      </div>
      {tab === "rag" && (
        <>
          <button className="btn btn-primary mb-2" onClick={load} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </button>
          <table className="table table-sm table-bordered">
            <thead className="table-light">
              <tr>
                <th>Query</th>
                <th>Chunk Count</th>
                <th>Avg. Confidence</th>
                <th>Fallback</th>
                <th>Glossary Boost</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td className="text-break" style={{ maxWidth: 200 }}>{log.query_text}</td>
                  <td>{log.retrieved_chunks?.length || 0}</td>
                  <td>{log.confidence_score_avg?.toFixed(2)}</td>
                  <td>{log.fallback_triggered ? "⚠️" : ""}</td>
                  <td>{log.glossary_matches?.length ? "✅" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
      {tab === "drift" && <AssistantDriftPanel slug={slug} />}
    </div>
  );
}
