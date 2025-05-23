import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CinemythComposer() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/cinemyths/")
      .then((res) => setItems(res.results || res))
      .catch(() => setItems([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Cinemyth Storylines</h5>
      <ul className="list-group">
        {items.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.storyline_title}
          </li>
        ))}
        {items.length === 0 && (
          <li className="list-group-item text-muted">No storylines.</li>
        )}
      </ul>
    </div>
  );
}
