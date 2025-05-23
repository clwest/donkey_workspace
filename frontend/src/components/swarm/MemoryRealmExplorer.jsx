import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryRealmExplorer() {
  const [realms, setRealms] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/memory-realms/");
        setRealms(res.results || res);
      } catch (err) {
        console.error("Failed to load memory realms", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Memory Realms</h5>
      <ul className="list-group">
        {realms.map((r) => (
          <li key={r.id} className="list-group-item">
            <strong>{r.zone_name}</strong> – {r.origin_myth_name || r.origin_myth}
          </li>
        ))}
        {realms.length === 0 && (
          <li className="list-group-item text-muted">No memory realms.</li>
        )}
      </ul>
    </div>
  );
}
