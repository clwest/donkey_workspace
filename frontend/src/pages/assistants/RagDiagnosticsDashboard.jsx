import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function RagDiagnosticsDashboard() {
  useAuthGuard();
  const { slug } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/rag_diagnostics/`)
      .then(setData)
      .catch(() => setData(null));
  }, [slug]);

  if (!data) return <div className="container my-4">Loading...</div>;

  return (
    <div className="container my-4">
      <h2 className="mb-3">RAG Diagnostics</h2>
      <div className="mb-2">
        <strong>Fallback Rate:</strong>{" "}
        <span className={data.fallback_pct > 40 ? "text-danger" : ""}>
          {data.fallback_pct.toFixed(1)}%
        </span>
      </div>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Anchor</th>
            <th>Fallbacks</th>
          </tr>
        </thead>
        <tbody>
          {data.top_failing.map((r) => (
            <tr key={r.expected_anchor}>
              <td>{r.expected_anchor}</td>
              <td>{r.fallbacks}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
