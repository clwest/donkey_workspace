import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CivilizationAtlas() {
  const [civs, setCivs] = useState([]);

  useEffect(() => {
    apiFetch("/agents/civilizations/")
      .then(setCivs)
      .catch(() => setCivs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Assistant Civilizations</h5>
      <ul className="list-group">
        {civs.map((c) => (
          <li key={c.id} className="list-group-item">
            <strong>{c.name}</strong> - {c.symbolic_domain}
          </li>
        ))}
        {civs.length === 0 && (
          <li className="list-group-item text-muted">No civilizations found.</li>
        )}
      </ul>
    </div>
  );
}
