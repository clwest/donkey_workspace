import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function TheocracyManager() {
  const [theocracies, setTheocracies] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/swarm/theocracies/");
        setTheocracies(res.results || res);
      } catch (err) {
        console.error("Failed to load theocracies", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Theocratic Governance</h5>
      <ul className="list-group">
        {theocracies.map((t) => (
          <li key={t.id} className="list-group-item">
            <strong>{t.ruling_entity_name || t.ruling_entity}</strong> – {t.canonized_myth_name || t.canonized_myth}
            <p className="mb-1 small">{t.seasonal_mandates}</p>
          </li>
        ))}
        {theocracies.length === 0 && (
          <li className="list-group-item text-muted">No theocratic models defined.</li>
        )}
      </ul>
    </div>
  );
}
