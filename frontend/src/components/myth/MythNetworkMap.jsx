import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythNetworkMap() {
  const [links, setLinks] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/agents/myth-links/`);
        setLinks(data || []);
      } catch (err) {
        console.error("Failed to load myth links", err);
      }
    }
    load();
  }, []);

  if (links.length === 0) return <div>No myth links recorded.</div>;

  return (
    <div className="card mb-3">
      <div className="card-header">Myth Network</div>
      <div className="card-body">
        <ul className="list-group">
          {links.map((l) => (
            <li key={l.id} className="list-group-item">
              {l.source_assistant} → {l.target_assistant} ({l.strength})
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
