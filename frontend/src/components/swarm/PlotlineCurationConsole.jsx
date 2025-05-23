import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PlotlineCurationConsole() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    apiFetch("/plotline-curation/")
      .then((res) => setEntries(res.results || res))
      .catch(() => setEntries([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Plotline Curations</h5>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.curated_arc_title} – {e.symbolic_convergence_score}
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No plotlines curated.</li>
        )}
      </ul>
    </div>
  );
}
