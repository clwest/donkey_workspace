import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ArchetypePulseDashboard() {
  const [pulses, setPulses] = useState([]);

  useEffect(() => {
    apiFetch("/agents/archetype-sync/")
      .then(setPulses)
      .catch(() => setPulses([]));
  }, []);

  return (
    <div className="container my-5">
      <h1>Archetype Sync Pulses</h1>
      <table className="table table-sm mt-3">
        <thead>
          <tr>
            <th>Entity</th>
            <th>Scope</th>
            <th>Archetypes</th>
          </tr>
        </thead>
        <tbody>
          {pulses.map((p) => (
            <tr key={p.id}>
              <td>{p.initiating_entity}</td>
              <td>{p.synchronization_scope}</td>
              <td>{JSON.stringify(p.synchronized_archetypes)}</td>
            </tr>
          ))}
          {pulses.length === 0 && (
            <tr>
              <td colSpan="3" className="text-muted">
                No pulses recorded.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
