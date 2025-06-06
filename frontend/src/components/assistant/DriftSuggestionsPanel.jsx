import { useEffect, useState } from "react";
import { fetchDriftSuggestions, reviewFirstMessageDrift } from "../../api/assistants";

export default function DriftSuggestionsPanel({ slug }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetchDriftSuggestions(slug);
      setItems(res);
    } catch (err) {
      console.error("Failed to load suggestions", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (slug) load();
  }, [slug]);

  const handleReview = async () => {
    setLoading(true);
    try {
      await reviewFirstMessageDrift(slug);
      await load();
    } catch (err) {
      console.error("Review failed", err);
    }
  };

  if (loading && items.length === 0) return <div>Loading suggestions...</div>;

  return (
    <div className="card mt-3">
      <div className="card-body">
        <h5 className="card-title">Drift Suggestions</h5>
        <button className="btn btn-sm btn-outline-primary mb-2" onClick={handleReview} disabled={loading}>
          {loading ? "Checking..." : "Review First Message Drift"}
        </button>
        <table className="table table-sm">
          <thead>
            <tr>
              <th>Anchor</th>
              <th>Action</th>
              <th>Score</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((s) => (
              <tr key={s.id}>
                <td>{s.anchor_slug || "—"}</td>
                <td>{s.suggested_action}</td>
                <td>{s.score?.toFixed(2)}</td>
                <td>{s.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
