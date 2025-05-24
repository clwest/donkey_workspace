import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BeliefForkViewer({ assistantId }) {
  const [forks, setForks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const url = assistantId
      ? `/assistants/${assistantId}/belief-forks/`
      : "/agents/belief-forks/";
    setLoading(true);
    apiFetch(url)
      .then((data) => {
        setForks(data.results || data);
        setError(null);
      })
      .catch((err) => {
        console.error("Failed to load belief forks", err);
        setError("No belief forks found");
        setForks([]);
      })
      .finally(() => setLoading(false));
  }, [assistantId]);

  return (
    <div className="my-3">
      <h5>Belief Forks</h5>
      {loading && <div>Loading forks...</div>}
      {error && !loading && (
        <div className="text-sm text-muted">{error}</div>
      )}
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
