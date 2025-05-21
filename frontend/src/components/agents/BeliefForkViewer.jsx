import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BeliefForkViewer() {
  const [forks, setForks] = useState([]);

  useEffect(() => {
    apiFetch("/agents/belief-forks/")
      .then(setForks)
      .catch(() => setForks([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Forks</h5>
      <ul className="list-group">
        {forks.map((f) => (
          <li key={f.id} className="list-group-item">
            {f.reason}
          </li>
        ))}
        {forks.length === 0 && (
          <li className="list-group-item text-muted">No belief forks found.</li>
        )}
      </ul>
    </div>
  );
}
