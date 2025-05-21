import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function TranscendentMythMap() {
  const [myths, setMyths] = useState([]);

  useEffect(() => {
    apiFetch("/agents/transcendent-myths/")
      .then(setMyths)
      .catch(() => setMyths([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Transcendent Myth Map</h5>
      <ul className="list-group">
        {myths.map((m) => (
          <li key={m.id} className="list-group-item">
            <strong>{m.title}</strong> — {m.mythic_axis}
          </li>
        ))}
        {myths.length === 0 && (
          <li className="list-group-item text-muted">No myths found.</li>
        )}
      </ul>
    </div>
  );
}
