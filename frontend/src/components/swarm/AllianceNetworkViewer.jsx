import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AllianceNetworkViewer() {
  const [alliances, setAlliances] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/alliances/");
        setAlliances(res.results || res);
      } catch (err) {
        console.error("Failed to load alliances", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Symbolic Alliances</h5>
      <ul className="list-group">
        {alliances.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.name}</strong>
          </li>
        ))}
        {alliances.length === 0 && (
          <li className="list-group-item text-muted">No alliances found.</li>
        )}
      </ul>
    </div>
  );
}
