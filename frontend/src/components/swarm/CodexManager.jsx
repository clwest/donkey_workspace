import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CodexManager() {
  const [codices, setCodices] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/codexes/");
        setCodices(res.results || res);
      } catch (err) {
        console.error("Failed to load codices", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Swarm Codices</h5>
      <ul className="list-group">
        {codices.map((c) => (
          <li key={c.id} className="list-group-item">
            <strong>{c.title}</strong> – {c.symbolic_domain}
          </li>
        ))}
        {codices.length === 0 && (
          <li className="list-group-item text-muted">No codices defined.</li>
        )}
      </ul>
    </div>
  );
}
