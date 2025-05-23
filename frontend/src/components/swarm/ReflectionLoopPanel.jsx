import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ReflectionLoopPanel() {
  const [loops, setLoops] = useState([]);

  useEffect(() => {
    apiFetch("/reflection-loops/")
      .then((res) => setLoops(res.results || res))
      .catch(() => setLoops([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Reflection Loops</h5>
      <ul className="list-group">
        {loops.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.triggered_by} – {l.belief_realignment_score}
          </li>
        ))}
        {loops.length === 0 && (
          <li className="list-group-item text-muted">No loops logged.</li>
        )}
      </ul>
    </div>
  );
}
