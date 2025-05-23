import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function FeedbackAnchorViewer() {
  const [anchors, setAnchors] = useState([]);

  useEffect(() => {
    apiFetch("/feedback-anchors/").then(setAnchors).catch(() => {});
  }, []);

  return (
    <div className="mb-3">
      <h5>Feedback Anchors</h5>
      <ul>
        {anchors.map((a) => (
          <li key={a.id}>{a.insight_yield}</li>
        ))}
      </ul>
    </div>
  );
}
