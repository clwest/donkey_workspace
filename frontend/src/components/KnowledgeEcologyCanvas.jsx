import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function KnowledgeEcologyCanvas() {
  const [maps, setMaps] = useState([]);

  useEffect(() => {
    apiFetch("/knowledge-ecology/").then(setMaps).catch(() => {});
  }, []);

  return (
    <div className="mb-3">
      <h5>Knowledge Ecology</h5>
      <ul>
        {maps.map((m) => (
          <li key={m.id}>{m.scope}</li>
        ))}
      </ul>
    </div>
  );
}
