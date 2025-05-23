import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryPalaceNavigator() {
  const [palaces, setPalaces] = useState([]);

  useEffect(() => {
    apiFetch("/agents/memory-palaces/")
      .then((res) => setPalaces(res.results || res))
      .catch(() => setPalaces([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Memory Palaces</h5>
      <ul className="list-group">
        {palaces.map((p) => (
          <li key={p.id} className="list-group-item">
            <strong>{p.assistant_name || p.assistant}</strong>
          </li>
        ))}
        {palaces.length === 0 && (
          <li className="list-group-item text-muted">No palaces available.</li>
        )}
      </ul>
    </div>
  );
}
