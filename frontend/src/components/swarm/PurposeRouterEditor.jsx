import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PurposeRouterEditor() {
  const [routes, setRoutes] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/assistants/purpose-routing/");
        setRoutes(res.results || res);
      } catch (err) {
        console.error("Failed to load routes", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Purpose Route Maps</h5>
      <ul className="list-group">
        {routes.map((r) => (
          <li key={r.id} className="list-group-item">
            <strong>{r.assistant_name || r.assistant}</strong>: {r.output_path}
          </li>
        ))}
        {routes.length === 0 && (
          <li className="list-group-item text-muted">No routes defined.</li>
        )}
      </ul>
    </div>
  );
}
