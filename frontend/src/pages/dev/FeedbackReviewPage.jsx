import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function FeedbackReviewPage() {
  const [items, setItems] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch("/memory/feedback/?status=pending");
        setItems(Array.isArray(data) ? data : data.results || []);
      } catch (err) {
        console.error("Failed to load feedback", err);
        setItems([]);
      }
    }
    load();
  }, []);

  const applyMutation = async (id) => {
    try {
      await apiFetch(`/memory/feedback/${id}/apply/`, { method: "POST" });
      setItems(items.filter((i) => i.id !== id));
    } catch (err) {
      console.error("apply failed", err);
    }
  };

  const rejectItem = async (id) => {
    try {
      await apiFetch(`/memory/feedback/${id}/`, { method: "PATCH", body: { status: "rejected" } });
      setItems(items.filter((i) => i.id !== id));
    } catch (err) {
      console.error("reject failed", err);
    }
  };

  const triggerReflection = async (id) => {
    try {
      await apiFetch(`/memory/feedback/${id}/trigger_reflection/`, { method: "POST" });
    } catch (err) {
      console.error("trigger reflection failed", err);
    }
  };

  if (items === null) {
    return <div className="container py-5">Loading...</div>;
  }

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between mb-3">
        <h2>Feedback Review</h2>
        <Link to="/dev-dashboard" className="btn btn-outline-secondary">
          ← Back
        </Link>
      </div>
      {items.length === 0 ? (
        <p className="text-muted">No pending feedback.</p>
      ) : (
        <table className="table table-sm">
          <thead>
            <tr>
              <th>Memory</th>
              <th>Suggestion</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((fb) => (
              <tr key={fb.id}>
                <td>{fb.memory}</td>
                <td>{fb.suggestion}</td>
                <td>{fb.status}</td>
                <td>
                  <button className="btn btn-success btn-sm me-1" onClick={() => applyMutation(fb.id)}>
                    Apply Mutation
                  </button>
                  <button className="btn btn-danger btn-sm me-1" onClick={() => rejectItem(fb.id)}>
                    Reject
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={() => triggerReflection(fb.id)}>
                    Reflect
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
