import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function EpistemicCurrentPanel() {
  const [currents, setCurrents] = useState([]);

  useEffect(() => {
    apiFetch("/epistemic-currents/").then(setCurrents).catch(() => {});
  }, []);

  return (
    <div className="mb-3">
      <h5>Epistemic Currents</h5>
      <ul>
        {currents.map((c) => (
          <li key={c.id}>
            {c.source} → {c.targets.join(", ")} ({c.current_strength})
          </li>
        ))}
      </ul>
    </div>
  );
}
