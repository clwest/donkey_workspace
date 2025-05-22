import { useEffect, useState } from "react";
import { fetchTribunalCases } from "../../api/agents";

export default function TribunalChamber() {
  const [cases, setCases] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchTribunalCases();
        setCases(data.results || data);
      } catch (err) {
        console.error("Failed to load tribunal cases", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Swarm Tribunals</h5>
      <ul className="list-group">
        {cases.map((c) => (
          <li key={c.id} className="list-group-item">
            {c.issue_type} – {c.verdict}
          </li>
        ))}
        {cases.length === 0 && (
          <li className="list-group-item text-muted">No tribunal cases.</li>
        )}
      </ul>
    </div>
  );
}
