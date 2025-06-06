import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import {
  runRagDiagnostics,
  fetchRagDiagnostics,
} from "../../api/assistants";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function AssistantRagSelfTestPage() {
  useAuthGuard();
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [running, setRunning] = useState(false);
  const [limit, setLimit] = useState(0);

  const load = async () => {
    try {
      const res = await fetchRagDiagnostics(slug);
      setData(res);
    } catch {
      setData(null);
    }
  };

  useEffect(() => {
    load();
  }, [slug]);

  const runTest = async () => {
    setRunning(true);
    try {
      const res = await runRagDiagnostics(slug, limit ? { limit } : undefined);
      setData(res);
      toast.success(`✅ RAG diagnostics completed for ${data?.assistant || slug}`);
    } catch (err) {
      console.error("RAG diagnostics failed", err);
      toast.error("Diagnostics failed");
    } finally {
      setRunning(false);
    }
  };

  const results = data?.anchor_stats || data?.results || [];

  const header = {
    total: results.length,
    pending: results.filter((r) => r.mutation_status === "pending").length,
    fallbacks: results.filter((r) => r.fallbacks > 0).length,
    drifted: results.filter((r) => r.status && r.status !== "healthy").length,
    avgScore:
      results.reduce((acc, r) => acc + (r.avg_score || 0), 0) /
        (results.length || 1),
  };

  return (
    <div className="container my-5">
      <h2 className="mb-3">RAG Diagnostics</h2>
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
        {data && (
          <>
            <button
              className="btn btn-sm btn-secondary"
              onClick={runTest}
              disabled={running}
            >
              {running ? "Running..." : "Re-run"}
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
                a.download = `${slug}_rag_diagnostics.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              Download JSON
            </button>
          </>
        )}
      </div>
      {data && (
        <>
          <div className="mb-3">
            <span className="me-3">
              <strong>Total Anchors Tested:</strong> {header.total}
            </span>
            <span className="me-3">
              <strong>Terms with Mutation Suggestions:</strong> {header.pending}
            </span>
            <span className="me-3">
              <strong>Terms with Fallbacks:</strong> {header.fallbacks}
            </span>
            <span className="me-3">
              <strong>Drifted Anchors:</strong> {header.drifted}
            </span>
            <span>
              <strong>Average Glossary Score:</strong> {header.avgScore.toFixed(2)}
            </span>
          </div>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Glossary Term</th>
                <th>Anchor Status</th>
                <th>Mutation Status</th>
                <th>Avg Score</th>
                <th>Fallback Count</th>
                <th>Mutation Score Delta</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, idx) => (
                <tr
                  key={idx}
                  className={
                    r.status === "failing"
                      ? "table-danger"
                      : r.fallbacks > 2
                      ? "table-warning"
                      : "table-success"
                  }
                >
                  <td>{r.label || r.anchor}</td>
                  <td>{r.status || "-"}</td>
                  <td>{r.mutation_status || "none"}</td>
                  <td>{(r.avg_score ?? r.final_score)?.toFixed(2)}</td>
                  <td>{r.fallbacks ?? r.fallback_count ?? 0}</td>
                  <td>{r.change || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
