import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function FeedbackSummaryPage() {
  const { slug } = useParams();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState("");

  useEffect(() => {
    async function load() {
      if (!slug) return;
      try {
        const data = await apiFetch(`/assistants/${slug}/feedback/`);
        setEntries(data || []);
      } catch (err) {
        console.error("Failed to load feedback", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  const filtered = typeFilter
    ? entries.filter((e) => e.feedback === typeFilter)
    : entries;

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>Feedback for {slug}</h2>
        <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
          Back
        </Link>
      </div>

      <div className="mb-3">
        <select
          className="form-select w-auto"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        >
          <option value="">All Types</option>
          <option value="perfect">Perfect</option>
          <option value="helpful">Helpful</option>
          <option value="not_helpful">Not Helpful</option>
          <option value="too_long">Too Long</option>
          <option value="too_short">Too Short</option>
          <option value="irrelevant">Irrelevant</option>
          <option value="unclear">Unclear</option>
        </select>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : filtered.length === 0 ? (
        <p className="text-muted">No feedback yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Thought</th>
              <th>Feedback</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((fb) => (
              <tr key={fb.id}>
                <td>{fb.thought}</td>
                <td>
                  <span className="badge bg-info text-dark">{fb.feedback}</span>
                </td>
                <td>{new Date(fb.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
