import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function ConstellationCanvas() {
  const [map, setMap] = useState(null);

  useEffect(() => {
    apiFetch("/constellation-map/").then(setMap);
  }, []);

  if (!map) return null;

  return (
    <div className="mb-3">
      <h5>Constellation Map</h5>
      {Object.entries(map.clusters).map(([mode, assistants]) => (
        <div key={mode} className="mb-2">
          <strong>{mode}</strong>: {assistants.map((a) => a.name).join(", ")}
        </div>
      ))}
    </div>
  );
}
