import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function ContinuityAnchorCard({ assistantId }) {
  const [anchors, setAnchors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = assistantId
      ? `/assistants/${assistantId}/continuity-anchors/`
      : "/memory/continuity-anchors/";
    apiFetch(url)
      .then((res) => setAnchors(res.results || res))
      .catch(() => setAnchors([]))
      .finally(() => setLoading(false));
  }, [assistantId]);

  if (loading) {
    return <div>Loading anchors...</div>;
  }

  return (
    <div className="card my-3">
      <div className="card-body">
        <h5 className="card-title">Continuity Anchors</h5>
        <ul className="list-group list-group-flush">
          {anchors.map((a) => (
            <li key={a.id} className="list-group-item">
              {a.label || a.id}
            </li>
          ))}
          {anchors.length === 0 && (
            <li className="list-group-item text-muted">No anchors found.</li>
          )}
        </ul>
      </div>
    </div>
  );
}
