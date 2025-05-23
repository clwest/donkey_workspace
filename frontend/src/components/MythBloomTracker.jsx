import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function MythBloomTracker() {
  const [blooms, setBlooms] = useState([]);

  useEffect(() => {
    apiFetch("/myth-blooms/").then(setBlooms);
  }, []);

  return (
    <div className="mb-3">
      <h5>Myth Bloom Nodes</h5>
      <ul>
        {blooms.map((b) => (
          <li key={b.id}>
            {b.bloom_name} ({b.participating_agents?.length || 0})
          </li>
        ))}
      </ul>
    </div>
  );
}
