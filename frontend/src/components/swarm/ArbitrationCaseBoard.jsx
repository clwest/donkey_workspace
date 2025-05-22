import { useEffect, useState } from "react";
import { fetchArbitrationCases } from "../../api/agents";

export default function ArbitrationCaseBoard() {
  const [cases, setCases] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchArbitrationCases();
        setCases(data.results || data);
      } catch (err) {
        console.error("Failed to load arbitration cases", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Arbitration Cases</h5>
      <ul className="list-group">
        {cases.map((c) => (
          <li key={c.id} className="list-group-item">
            {c.verdict} – {c.resolution_summary || "pending"}
          </li>
        ))}
        {cases.length === 0 && (
          <li className="list-group-item text-muted">No arbitration cases.</li>
        )}
      </ul>
    </div>
  );
}
