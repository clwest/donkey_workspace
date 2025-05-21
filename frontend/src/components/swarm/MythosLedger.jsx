import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythosLedger({ assistantId }) {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`/swarm/mythos/`, {
          params: assistantId ? { assistant: assistantId } : {},
        });
        setEntries(res.results || res);
      } catch (err) {
        console.error("Failed to load mythos", err);
      }
    }
    load();
  }, [assistantId]);

  if (!entries.length) {
    return <div className="alert alert-secondary">No myths recorded.</div>;
  }

  return (
    <ul className="list-group">
      {entries.map((m) => (
        <li key={m.id} className="list-group-item">
          <strong>{m.myth_title}</strong>
          <p className="mb-1 small">{m.myth_summary}</p>
        </li>
      ))}
    </ul>
  );
}
