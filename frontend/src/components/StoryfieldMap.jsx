import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function StoryfieldMap() {
  const [zones, setZones] = useState([]);
  useEffect(() => {
    apiFetch("/storyfields/").then(setZones);
  }, []);

  return (
    <div className="p-2 border rounded">
      <h5>Storyfield Zones</h5>
      <ul>
        {zones.map((z) => (
          <li key={z.id}>{z.zone_name} - {z.resonance_threshold}</li>
        ))}
      </ul>
    </div>
  );
}
