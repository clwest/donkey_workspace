import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythDiplomacyHub() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    apiFetch("/agents/myth-diplomacy/")
      .then(setSessions)
      .catch(() => setSessions([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Diplomacy Sessions</h5>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Topic</th>
            <th>Factions</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map((s) => (
            <tr key={s.id}>
              <td>{s.topic}</td>
              <td>{(s.factions || []).join(", ")}</td>
              <td>{s.status}</td>
            </tr>
          ))}
          {sessions.length === 0 && (
            <tr>
              <td colSpan="3" className="text-muted">
                No diplomacy in progress.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
