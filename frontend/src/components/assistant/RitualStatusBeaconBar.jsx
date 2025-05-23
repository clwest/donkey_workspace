import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualStatusBeaconBar({ assistantId }) {
  const [beacons, setBeacons] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${assistantId}/ritual-beacons/`);
        setBeacons(res);
      } catch (err) {
        console.error("Failed to load ritual beacons", err);
      }
    }
    load();
  }, [assistantId]);

  return (
    <div className="beacon-bar">
      {beacons.map((b) => (
        <span
          key={b.id}
          title={b.tooltip}
          className={`beacon ${b.availability_state}`}
        >
          {b.ritual_blueprint_name}
        </span>
      ))}
    </div>
  );
}
