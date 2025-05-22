import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CosmologyRoleBrowser() {
  const [roles, setRoles] = useState([]);

  useEffect(() => {
    apiFetch("/cosmological-roles/")
      .then((data) => setRoles(data.results || data))
      .catch(() => setRoles([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Cosmological Roles</h5>
      <ul className="list-group">
        {roles.map((r) => (
          <li key={r.id} className="list-group-item">
            <strong>{r.name}</strong>
          </li>
        ))}
        {roles.length === 0 && (
          <li className="list-group-item text-muted">No roles defined.</li>
        )}
      </ul>
    </div>
  );
}
