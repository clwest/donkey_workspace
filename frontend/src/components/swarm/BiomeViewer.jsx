import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BiomeViewer() {
  const [biomes, setBiomes] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/swarm/biomes/");
        setBiomes(res.results || res);
      } catch (err) {
        console.error("Failed to load biomes", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Biomes</h5>
      <ul className="list-group">
        {biomes.map((b) => (
          <li key={b.id} className="list-group-item">
            <strong>{b.name}</strong>
            <p className="mb-1 small">
              {Object.keys(b.core_traits || {}).join(", ")}
            </p>
          </li>
        ))}
        {biomes.length === 0 && (
          <li className="list-group-item text-muted">No biomes found.</li>
        )}
      </ul>
    </div>
  );
}
