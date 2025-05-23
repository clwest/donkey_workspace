import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { fetchAvailableRituals } from "../../api/agents";

export default function RitualLaunchpadPanel({ assistantId }) {
  const [rituals, setRituals] = useState([]);

  useEffect(() => {
    fetchAvailableRituals(assistantId ? { assistant: assistantId } : {})
      .then((res) => setRituals(res.results || res))
      .catch(() => setRituals([]));
  }, [assistantId]);

  const handleLaunch = (id) => {
    apiFetch(`/mythos/ritual-launchpads/${id}/launch/`, { method: "POST" }).then(
      () => alert("Ritual launched")
    );
  };

  return (
    <div className="p-2 border rounded">
      <h5>Ritual Launchpads</h5>
      <ul className="list-group">
        {rituals.map((r) => (
          <li key={r.id} className="list-group-item d-flex justify-content-between align-items-center">
            <span>{r.title}</span>
            <button className="btn btn-sm btn-primary" onClick={() => handleLaunch(r.id)}>
              Launch
            </button>
          </li>
        ))}
        {rituals.length === 0 && (
          <li className="list-group-item text-muted">No rituals available.</li>
        )}
      </ul>
    </div>
  );
}
