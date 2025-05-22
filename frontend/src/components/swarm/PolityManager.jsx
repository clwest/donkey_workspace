import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PolityManager() {
  const [polities, setPolities] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/polities/");
        setPolities(res.results || res);
      } catch (err) {
        console.error("Failed to load polities", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Assistant Polities</h5>
      <ul className="list-group">
        {polities.map((p) => (
          <li key={p.id} className="list-group-item">
            <strong>{p.name}</strong> – {p.symbolic_legitimacy_score}
          </li>
        ))}
        {polities.length === 0 && (
          <li className="list-group-item text-muted">No polities defined.</li>
        )}
      </ul>
    </div>
  );
}
