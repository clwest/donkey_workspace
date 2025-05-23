import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DreamframePlayer() {
  const [segments, setSegments] = useState([]);

  useEffect(() => {
    apiFetch("/dreamframes/")
      .then((res) => setSegments(res.results || res))
      .catch(() => setSegments([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Dreamframe Segments</h5>
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
