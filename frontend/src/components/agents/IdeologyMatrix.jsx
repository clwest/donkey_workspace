import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function IdeologyMatrix() {
  const [assistants, setAssistants] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/")
      .then(setAssistants)
      .catch(() => setAssistants([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ideology Matrix</h5>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Name</th>
            <th>Tone</th>
            <th>Stance</th>
          </tr>
        </thead>
        <tbody>
          {assistants.map((a) => (
            <tr key={a.id}>
              <td>{a.name}</td>
              <td>{a.ideology?.tone || "-"}</td>
              <td>{a.ideology?.stance || "-"}</td>
            </tr>
          ))}
          {assistants.length === 0 && (
            <tr>
              <td colSpan="3" className="text-muted">
                No assistants found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
