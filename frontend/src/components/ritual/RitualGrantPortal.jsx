import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualGrantPortal() {
  const [grants, setGrants] = useState([]);

  useEffect(() => {
    apiFetch("/ritual/grants/")
      .then((res) => setGrants(res.results || res))
      .catch(() => {});
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Grants</h5>
      <ul className="list-group">
        {grants.map((g) => (
          <li key={g.id} className="list-group-item">
            <strong>{g.title}</strong>
            <span className="ms-2 text-muted small">{g.status}</span>
          </li>
        ))}
        {grants.length === 0 && (
          <li className="list-group-item text-muted">No grants found.</li>
        )}
      </ul>
    </div>
  );
}
