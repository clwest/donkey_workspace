import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import useAuthGuard from "../../hooks/useAuthGuard";
import { fetchRagDiagnosticLogs } from "../../api/assistants";

export default function AssistantRagDiagnosticsConsolePage() {
  useAuthGuard();
  const { slug } = useParams();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetchRagDiagnosticLogs({ assistant: slug });
      setLogs(res.results || []);
    } catch (err) {
      console.error("Failed to load diagnostic logs", err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [slug]);

  return (
    <div className="container my-4">
      <h2 className="mb-3">RAG Diagnostic Logs</h2>
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
    </div>
  );
}
