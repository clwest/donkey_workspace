import { useEffect, useState } from "react";
import { fetchCosmologies } from "../../api/agents";

export default function CosmologyExplorer() {
  const [cosmos, setCosmos] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchCosmologies();
        setCosmos(data.results || data);
      } catch (err) {
        console.error("Failed to load cosmologies", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Swarm Cosmologies</h5>
      <ul className="list-group">
        {cosmos.map((c) => (
          <li key={c.id} className="list-group-item">
            <strong>{c.name}</strong>
          </li>
        ))}
        {cosmos.length === 0 && (
          <li className="list-group-item text-muted">No cosmologies defined.</li>
        )}
      </ul>
    </div>
  );
}
