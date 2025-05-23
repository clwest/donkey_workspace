import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualSyncManager() {
  const [pulses, setPulses] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/ritual-sync/");
        setPulses(res.results || res);
      } catch (err) {
        console.error("Failed to load ritual sync pulses", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Sync Pulses</h5>
      <ul className="list-group">
        {pulses.map((p) => (
          <li key={p.id} className="list-group-item">
            <strong>{p.pulse_id}</strong> – {p.phase_trigger}
          </li>
        ))}
        {pulses.length === 0 && (
          <li className="list-group-item text-muted">No sync pulses active.</li>
        )}
      </ul>
    </div>
  );
}
