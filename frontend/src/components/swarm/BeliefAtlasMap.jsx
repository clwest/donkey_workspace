import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BeliefAtlasMap() {
  const [atlases, setAtlases] = useState([]);

  useEffect(() => {
    apiFetch("/agents/belief-atlases/")
      .then(setAtlases)
      .catch(() => setAtlases([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Atlas Snapshots</h5>
      <ul className="list-group">
        {atlases.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.epoch}</strong> – {a.scope}
          </li>
        ))}
        {atlases.length === 0 && (
          <li className="list-group-item text-muted">No atlas data.</li>
        )}
      </ul>
    </div>
  );
}
