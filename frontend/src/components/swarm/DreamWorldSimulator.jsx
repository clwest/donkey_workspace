import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DreamWorldSimulator() {
  const [worlds, setWorlds] = useState([]);

  useEffect(() => {
    apiFetch("/dream-worlds/")
      .then((res) => setWorlds(res.results || res))
      .catch(() => setWorlds([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Dream Worlds</h5>
      <ul className="list-group">
        {worlds.map((w) => (
          <li key={w.id} className="list-group-item">
            {w.world_name}
          </li>
        ))}
        {worlds.length === 0 && (
          <li className="list-group-item text-muted">No dream worlds.</li>
        )}
      </ul>
    </div>
  );
}
