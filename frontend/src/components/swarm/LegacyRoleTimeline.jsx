import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LegacyRoleTimeline() {
  const [roles, setRoles] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/legacy-roles/");
        setRoles(res.results || res);
      } catch (err) {
        console.error("Failed to load legacy roles", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Legacy Roles</h5>
      <ul className="list-group">
        {roles.map((r) => (
          <li key={r.id} className="list-group-item">
            <strong>{r.role_name}</strong> – {r.status}
          </li>
        ))}
        {roles.length === 0 && (
          <li className="list-group-item text-muted">No legacy roles found.</li>
        )}
      </ul>
    </div>
  );
}
