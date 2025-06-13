import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchToolConfidence, recommendToolChanges } from "../../api/assistants";
import apiFetch from "../../utils/apiClient";

export default function ToolConfidenceDashboard() {
  const { slug } = useParams();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recommend, setRecommend] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchToolConfidence(slug);
      setRows(data.results || []);
    } catch (err) {
      console.error("Failed to load", err);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async () => {
    try {
      const data = await recommendToolChanges(slug);
      setRecommend(data.results || []);
    } catch (err) {
      console.error("Failed to recommend", err);
    }
  };

  useEffect(() => {
    load();
  }, [slug]);

  return (
    <div className="container my-5">
      <h2 className="mb-3">Tool Confidence Dashboard</h2>
      <button className="btn btn-outline-secondary mb-2" onClick={load} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh"}
      </button>
      <button className="btn btn-outline-primary ms-2 mb-2" onClick={handleRecommend}>
        Suggest Tool Changes
      </button>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Tool</th>
            <th>Avg Score</th>
            <th>Usage</th>
            <th>Favorite</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.tool} className={r.avg_confidence < 0.3 ? "table-warning" : ""}>
              <td>{r.name}</td>
              <td>{r.avg_confidence.toFixed(2)}</td>
              <td>{r.usage_count}</td>
              <td>{r.favorite ? "⭐" : ""}</td>
            </tr>
          ))}
          {rows.length === 0 && !loading && (
            <tr>
              <td colSpan="4" className="text-muted">
                No data.
              </td>
            </tr>
          )}
        </tbody>
      </table>
      {recommend && (
        <pre className="mt-3 bg-light p-2 border rounded">
          {JSON.stringify(recommend, null, 2)}
        </pre>
      )}
    </div>
  );
}
