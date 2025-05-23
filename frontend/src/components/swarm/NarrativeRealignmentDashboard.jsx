import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function NarrativeRealignmentDashboard() {
  const [proposals, setProposals] = useState([]);

  useEffect(() => {
    apiFetch("/agents/realignment-proposals/")
      .then((data) => setProposals(data.results || data))
      .catch(() => setProposals([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Narrative Realignment Proposals</h5>
      <ul className="list-group">
        {proposals.map((p) => (
          <li key={p.id} className="list-group-item">
            {p.reason}
          </li>
        ))}
        {proposals.length === 0 && (
          <li className="list-group-item text-muted">No proposals found.</li>
        )}
      </ul>
    </div>
  );
}
