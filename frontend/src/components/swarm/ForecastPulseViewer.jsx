import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ForecastPulseViewer() {
  const [pulses, setPulses] = useState([]);

  useEffect(() => {
    apiFetch("/agents/mythic-forecast/")
      .then(setPulses)
      .catch(() => setPulses([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Mythic Forecast Pulses</h5>
      <ul className="list-group">
        {pulses.map((p) => (
          <li key={p.id} className="list-group-item">
            <strong>{p.pulse_range}</strong> – {p.narrative_conditions}
          </li>
        ))}
        {pulses.length === 0 && (
          <li className="list-group-item text-muted">No pulses logged.</li>
        )}
      </ul>
    </div>
  );
}
