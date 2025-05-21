import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";


export default function MissionArchetypeBrowser() {
  const [archetypes, setArchetypes] = useState([]);

  useEffect(() => {
    apiFetch("/agents/mission-archetypes/")
      .then(setArchetypes)
      .catch(() => setArchetypes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Mission Archetypes</h5>
      <ul className="list-group">
        {archetypes.map((a) => (
          <li key={a.id} className="list-group-item d-flex justify-content-between align-items-center">
            <span>{a.name}</span>
            <button className="btn btn-sm btn-outline-primary">Clone</button>

          </li>
        ))}
        {archetypes.length === 0 && (
          <li className="list-group-item text-muted">No archetypes.</li>
        )}
      </ul>
    </div>
  );
}

