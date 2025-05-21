import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CosmogenesisChronicle() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    apiFetch("/agents/cosmogenesis/")
      .then(setEvents)
      .catch(() => setEvents([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Cosmogenesis Chronicle</h5>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Name</th>
            <th>Lifecycle</th>
            <th>Myth Root</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <tr key={e.id}>
              <td>{e.name}</td>
              <td>{e.lifecycle}</td>
              <td>{e.myth_root_title}</td>
            </tr>
          ))}
          {events.length === 0 && (
            <tr>
              <td colSpan="3" className="text-muted">
                No events recorded.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
