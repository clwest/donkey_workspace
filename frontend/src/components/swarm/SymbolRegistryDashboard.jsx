import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SymbolRegistryDashboard() {
  const [resources, setResources] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/symbolic-resources/");
        setResources(res.results || res);
      } catch (err) {
        console.error("Failed to load symbolic resources", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Symbol Registry</h5>
      <ul className="list-group">
        {resources.map((r) => (
          <li key={r.id} className="list-group-item">
            <strong>{r.unique_id}</strong> – {r.resource_type}
          </li>
        ))}
        {resources.length === 0 && (
          <li className="list-group-item text-muted">No resources registered.</li>
        )}
      </ul>
    </div>
  );
}
