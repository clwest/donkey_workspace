import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CosmoAlignmentTracker() {
  const [maps, setMaps] = useState([]);

  useEffect(() => {
    apiFetch("/cosmo-alignment/")
      .then((res) => setMaps(res.results || res))
      .catch(() => setMaps([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Cosmo-Economic Alignment</h5>
      <ul className="list-group">
        {maps.map((m) => (
          <li key={m.id} className="list-group-item">
            {m.mythic_zone} – {m.symbolic_alignment_rating}
          </li>
        ))}
        {maps.length === 0 && (
          <li className="list-group-item text-muted">No alignment data.</li>
        )}
      </ul>
    </div>
  );
}
