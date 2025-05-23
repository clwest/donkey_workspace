import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function NarrativeWalkthroughPlayer() {
  const [walks, setWalks] = useState([]);

  useEffect(() => {
    apiFetch("/belief-walkthroughs/")
      .then((res) => setWalks(res.results || res))
      .catch(() => setWalks([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Narrative Walkthroughs</h5>
      <ul className="list-group">
        {walks.map((w) => (
          <li key={w.id} className="list-group-item">
            {w.walkthrough_title}
          </li>
        ))}
        {walks.length === 0 && (
          <li className="list-group-item text-muted">No walkthroughs.</li>
        )}
      </ul>
    </div>
  );
}
