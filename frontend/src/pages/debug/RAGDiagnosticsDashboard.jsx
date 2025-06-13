import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function RAGDiagnosticsDashboard() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const assistants = await apiFetch("/assistants/");
        const data = await Promise.all(
          assistants.map(async (a) => {
            try {
              const report = await apiFetch(`/assistants/${a.slug}/diagnostic_report/`);
              return { name: a.name, slug: a.slug, report };
            } catch {
              return { name: a.name, slug: a.slug, report: null };
            }
          })
        );
        setRows(data);
      } catch {
        setRows([]);
      }
    }
    load();
  }, []);

  return (
    <div className="container my-4">
      <h3 className="mb-3">RAG Diagnostic Reports</h3>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Assistant</th>
            <th>Glossary</th>
            <th>Avg Score</th>
            <th>Fallback</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.slug}>
              <td>{r.name}</td>
              {r.report ? (
                <>
                  <td>{(r.report.glossary_success_rate * 100).toFixed(0)}%</td>
                  <td>{r.report.avg_chunk_score.toFixed(2)}</td>
                  <td>{(r.report.fallback_rate * 100).toFixed(0)}%</td>
                  <td>
                    <Link
                      to={`/assistants/${r.slug}/rag_debug/`}
                      className="btn btn-sm btn-primary me-1"
                    >
                      Logs
                    </Link>
                    <Link
                      to={`/assistants/${r.slug}/rag-inspector`}
                      className="btn btn-sm btn-secondary"
                    >
                      Inspector
                    </Link>
                  </td>
                </>
              ) : (
                <td colSpan="4" className="text-muted">
                  No report
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
