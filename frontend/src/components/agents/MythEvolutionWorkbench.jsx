import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythEvolutionWorkbench() {
  const [protocols, setProtocols] = useState([]);

  useEffect(() => {
    apiFetch("/agents/local-myth-protocols/")
      .then(setProtocols)
      .catch(() => setProtocols([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Evolution Workbench</h5>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Base Lore</th>
            <th>Guild</th>
            <th>Resolved</th>
          </tr>
        </thead>
        <tbody>
          {protocols.map((p) => (
            <tr key={p.id}>
              <td>{p.base_lore_title || p.base_lore}</td>
              <td>{p.steward_guild_name || p.steward_guild}</td>
              <td>{p.resolved ? "Yes" : "No"}</td>
            </tr>
          ))}
          {protocols.length === 0 && (
            <tr>
              <td colSpan="3" className="text-muted">
                No protocols
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
