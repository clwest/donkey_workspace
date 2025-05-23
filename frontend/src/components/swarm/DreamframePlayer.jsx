import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DreamframePlayer({ assistantId }) {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = assistantId
      ? `/assistants/${assistantId}/dreamframes/`
      : "/dreamframes/";
    apiFetch(url)
      .then((res) => setSegments(res.results || res))
      .catch(() => setSegments([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="my-3">
      <h5>Dreamframe Segments</h5>
      {loading && <div>Loading dreamframes...</div>}
      <ul className="list-group">
        {segments.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.visual_style}
          </li>
        ))}
        {segments.length === 0 && (
          <li className="list-group-item text-muted">No segments.</li>
        )}
      </ul>
    </div>
  );
}
