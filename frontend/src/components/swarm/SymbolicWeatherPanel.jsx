import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SymbolicWeatherPanel() {
  const [fronts, setFronts] = useState([]);

  useEffect(() => {
    apiFetch("/agents/symbolic-weather/")
      .then(setFronts)
      .catch(() => setFronts([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Symbolic Weather Fronts</h5>
      <ul className="list-group">
        {fronts.map((f) => (
          <li key={f.id} className="list-group-item">
            <strong>{f.name}</strong> – {f.projected_effects}
          </li>
        ))}
        {fronts.length === 0 && (
          <li className="list-group-item text-muted">No active fronts.</li>
        )}
      </ul>
    </div>
  );
}
