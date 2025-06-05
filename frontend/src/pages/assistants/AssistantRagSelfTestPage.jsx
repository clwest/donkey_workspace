import { useState } from "react";
import { useParams } from "react-router-dom";
import { runRagSelfTest } from "../../api/assistants";

export default function AssistantRagSelfTestPage() {
  const { slug } = useParams();
  const [results, setResults] = useState([]);
  const [running, setRunning] = useState(false);
  const [limit, setLimit] = useState(0);

  const runTest = async () => {
    setRunning(true);
    try {
      const res = await runRagSelfTest(slug, limit ? { limit } : undefined);
      setResults(res.results || res);
    } catch (err) {
      console.error("RAG self test failed", err);
      setResults([]);
    } finally {
      setRunning(false);
    }
  };

  const passedCount = results.filter((r) => r.success).length;

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
        <button className="btn btn-primary" onClick={runTest} disabled={running}>
          {running ? "Running..." : "Run RAG Test"}
        </button>
      </div>
      {results.length > 0 && (
        <>
          <p>
            {passedCount}/{results.length} passed
          </p>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Glossary Term</th>
                <th>Matched Chunks</th>
                <th>Fallback</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, idx) => (
                <tr
                  key={idx}
                  className={r.success ? "table-success" : r.fallback_reason ? "table-warning" : "table-danger"}
                >
                  <td>{r.glossary_term}</td>
                  <td>{(r.matched_chunks || []).length}</td>
                  <td>{r.fallback_reason || ""}</td>
                  <td>{r.duration_ms} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
