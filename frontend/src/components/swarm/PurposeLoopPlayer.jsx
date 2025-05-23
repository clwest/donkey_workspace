import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PurposeLoopPlayer() {
  const [loops, setLoops] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/simulation/purpose-loops/")
      .then((res) => setLoops(res.results || res))
      .catch(() => setLoops([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="my-3">
      <h5>Purpose Loop Engines</h5>
      {loading && <div>Loading loops...</div>}
      <ul className="list-group">
        {loops.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.loop_condition}
          </li>
        ))}
        {loops.length === 0 && (
          <li className="list-group-item text-muted">No purpose loops.</li>
        )}
      </ul>
    </div>
  );
}
