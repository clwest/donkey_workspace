import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DiplomacyTable() {
  const [treaties, setTreaties] = useState([]);

  useEffect(() => {
    apiFetch("/agents/swarm-treaties/")
      .then(setTreaties)
      .catch(() => setTreaties([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Swarm Treaties</h5>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Name</th>
            <th>Participants</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {treaties.map((t) => (
            <tr key={t.id}>
              <td>{t.name}</td>
              <td>{(t.participants || []).join(", ")}</td>
              <td>{t.status}</td>
            </tr>
          ))}
          {treaties.length === 0 && (
            <tr>
              <td colSpan="3" className="text-muted">
                No treaties found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
