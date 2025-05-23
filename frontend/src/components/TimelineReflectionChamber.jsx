import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function TimelineReflectionChamber() {
  const [rites, setRites] = useState([]);

  useEffect(() => {
    apiFetch("/timeline-reflection/").then(setRites);
  }, []);

  return (
    <div className="mb-3">
      <h5>Cross-Timeline Reflection Rites</h5>
      <ul>
        {rites.map((r) => (
          <li key={r.id}>
            {r.ritual_summary} ({r.symbolic_convergence_score})
          </li>
        ))}
      </ul>
    </div>
  );
}
