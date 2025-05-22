import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DreamPurposeSimPanel() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/dream-negotiation/");
        setSessions(res.results || res);
      } catch (err) {
        console.error("Failed to load negotiations", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Dream Purpose Negotiations</h5>
      <ul className="list-group">
        {sessions.map((s) => (
          <li key={s.id} className="list-group-item">
            <strong>{s.proposed_purpose_update}</strong>
          </li>
        ))}
        {sessions.length === 0 && (
          <li className="list-group-item text-muted">No sessions running.</li>
        )}
      </ul>
    </div>
  );
}
