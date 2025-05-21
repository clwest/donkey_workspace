import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LoreLedger() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/lore/");
        setEntries(res || []);
      } catch (err) {
        console.error("Failed to load lore", err);
      }
    }
    load();
  }, []);

  return (
    <div>
      <h3>Lore Ledger</h3>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.title}</strong>
            {e.is_canon && (
              <span className="badge bg-success ms-1">Canon</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
