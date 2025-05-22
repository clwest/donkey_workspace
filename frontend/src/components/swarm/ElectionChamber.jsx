import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ElectionChamber() {
  const [elections, setElections] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/elections/");
        setElections(res.results || res);
      } catch (err) {
        console.error("Failed to load elections", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Elections</h5>
      <ul className="list-group">
        {elections.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.election_type}</strong> – {e.polity_name || e.polity}
          </li>
        ))}
        {elections.length === 0 && (
          <li className="list-group-item text-muted">No elections recorded.</li>
        )}
      </ul>
    </div>
  );
}
