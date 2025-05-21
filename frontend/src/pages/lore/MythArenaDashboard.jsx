import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythArenaDashboard() {
  const [arenas, setArenas] = useState([]);

  useEffect(() => {
    apiFetch("/agents/myth-arenas/")
      .then(setArenas)
      .catch(() => setArenas([]));
  }, []);

  return (
    <div className="container my-5">
      <h1>Myth Simulation Arenas</h1>
      <table className="table table-sm mt-3">
        <thead>
          <tr>
            <th>Name</th>
            <th>Scenario</th>
            <th>Outcome</th>
          </tr>
        </thead>
        <tbody>
          {arenas.map((a) => (
            <tr key={a.id}>
              <td>{a.name}</td>
              <td>{a.simulated_scenario.slice(0, 40)}</td>
              <td>{a.outcome_summary || "Pending"}</td>
            </tr>
          ))}
          {arenas.length === 0 && (
            <tr>
              <td colSpan="3" className="text-muted">
                No simulations run yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
