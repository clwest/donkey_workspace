import { useState } from "react";
import { useParams } from "react-router-dom";
import { runRagSelfTest } from "../../api/assistants";

export default function AssistantRagSelfTestPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [running, setRunning] = useState(false);
  const [limit, setLimit] = useState(0);

  const runTest = async () => {
    setRunning(true);
    try {
      const res = await runRagSelfTest(slug, limit ? { limit } : undefined);
      setData(res);
    } catch (err) {
      console.error("RAG self test failed", err);
      setData(null);
    } finally {
      setRunning(false);
    }
  };

  const results = data?.results || [];
  const passedCount = results.filter((r) => r.status === "ok").length;

  return (
    <div className="container my-5">
      <h2 className="mb-3">RAG Diagnostic Runner</h2>
      <div className="d-flex align-items-center mb-3 gap-2">
        <label className="form-label mb-0">Limit</label>
        <input
          type="number"
          className="form-control form-control-sm"
          style={{ width: "80px" }}
          value={limit}
          onChange={(e) => setLimit(parseInt(e.target.value) || 0)}
        />
        <button
          className="btn btn-primary"
          onClick={runTest}
          disabled={running}
        >
          {running ? "Running..." : "Run RAG Test"}
        </button>
      </div>
      {data && (
        <>
          <div className="mb-2 d-flex align-items-center gap-2">
            <strong>Assistant:</strong> {data.assistant}
            <span>Anchors tested: {data.tested}</span>
            <span>Issues: {data.issues_found}</span>
            <span>Pass rate: {(data.pass_rate * 100).toFixed(1)}%</span>
            <span>Time: {data.duration.toFixed(1)}s</span>
            <button
              className="btn btn-sm btn-secondary"
              onClick={runTest}
              disabled={running}
            >
              {running ? "Running..." : "Re-run Last Test"}
            </button>
            <button
              className="btn btn-sm btn-outline-primary"
              onClick={() => {
                const blob = new Blob([JSON.stringify(data, null, 2)], {
                  type: "application/json",
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `${slug}_rag_diagnostic.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              Export as JSON
            </button>
            {data.issues_found > 0 && (
              <a
                className="btn btn-sm btn-outline-info"
                href={`/assistants/${slug}/rag-inspector`}
              >
                View in Inspector
              </a>
            )}
          </div>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Anchor Term</th>
                <th>Hits</th>
                <th>Fallbacks</th>
                <th>Final Score</th>
                <th>Glossary Boost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, idx) => (
                <tr key={idx}>
                  <td>{r.anchor}</td>
                  <td>{r.hits}</td>
                  <td>{r.fallbacks}</td>
                  <td>{r.final_score.toFixed(3)}</td>
                  <td>{r.glossary_boost.toFixed(2)}</td>
                  <td>
                    {r.status === "ok" && (
                      <span className="badge bg-success">✅ OK</span>
                    )}
                    {r.status === "fallback" && (
                      <span className="badge bg-warning text-dark">
                        ⚠️ Fallback
                      </span>
                    )}
                    {r.status === "miss" && (
                      <span className="badge bg-danger">❌ Miss</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
