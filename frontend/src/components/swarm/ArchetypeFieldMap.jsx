import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ArchetypeFieldMap() {
  const [clusters, setClusters] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/archetype-fields/");
        setClusters(res.results || res);
      } catch (err) {
        console.error("Failed to load archetype fields", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Archetype Fields</h5>
      <ul className="list-group">
        {clusters.map((c) => (
          <li key={c.id} className="list-group-item">
            <strong>{c.cluster_name}</strong> – {c.resonance_score}
          </li>
        ))}
        {clusters.length === 0 && (
          <li className="list-group-item text-muted">No archetype clusters.</li>
        )}
      </ul>
    </div>
  );
}
