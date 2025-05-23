import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BeliefVectorNavigator() {
  const [vectors, setVectors] = useState([]);

  useEffect(() => {
    apiFetch("/navigation-vectors/")
      .then((res) => setVectors(res.results || res))
      .catch(() => setVectors([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Navigation Vectors</h5>
      <ul className="list-group">
        {vectors.map((v) => (
          <li key={v.id} className="list-group-item">
            {v.assistant} – score: {v.alignment_score}
          </li>
        ))}
        {vectors.length === 0 && (
          <li className="list-group-item text-muted">No vectors available.</li>
        )}
      </ul>
    </div>
  );
}
