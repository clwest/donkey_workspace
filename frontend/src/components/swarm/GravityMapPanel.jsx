import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function GravityMapPanel() {
  const [wells, setWells] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/gravity-wells/");
        setWells(res.results || res);
      } catch (err) {
        console.error("Failed to load gravity wells", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Symbolic Gravity Wells</h5>
      <ul className="list-group">
        {wells.map((w) => (
          <li key={w.id} className="list-group-item">
            {w.source_memory_title || w.source_memory} – radius {w.influence_radius}
          </li>
        ))}
        {wells.length === 0 && (
          <li className="list-group-item text-muted">No active wells.</li>
        )}
      </ul>
    </div>
  );
}
