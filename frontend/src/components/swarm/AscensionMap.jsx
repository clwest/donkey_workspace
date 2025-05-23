import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AscensionMap() {
  const [structures, setStructures] = useState([]);

  useEffect(() => {
    apiFetch("/agents/ascension-structures/")
      .then((res) => setStructures(res.results || res))
      .catch(() => setStructures([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ascension Structures</h5>
      <ul className="list-group">
        {structures.map((s) => (
          <li key={s.id} className="list-group-item">
            <strong>{s.name}</strong> – {s.ascension_state}
          </li>
        ))}
        {structures.length === 0 && (
          <li className="list-group-item text-muted">No ascension data.</li>
        )}
      </ul>
    </div>
  );
}
