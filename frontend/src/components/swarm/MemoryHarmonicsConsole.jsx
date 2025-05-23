import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryHarmonicsConsole() {
  const [pulses, setPulses] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/memory-harmonics/");
        setPulses(res.results || res);
      } catch (err) {
        console.error("Failed to load harmonic pulses", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Memory Harmonics</h5>
      <ul className="list-group">
        {pulses.map((p) => (
          <li key={p.id} className="list-group-item">
            {p.pulse_id} – coherence {p.phase_coherence_level}
          </li>
        ))}
        {pulses.length === 0 && (
          <li className="list-group-item text-muted">No harmonic pulses.</li>
        )}
      </ul>
    </div>
  );
}
