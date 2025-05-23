import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function BraidedMemoryViewer() {
  const [strands, setStrands] = useState([]);

  useEffect(() => {
    apiFetch("/memory/memory-braids/")
      .then((d) => setStrands(d.results || d))
      .catch(() => setStrands([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Braided Memory Strands</h5>
      <ul className="list-group">
        {strands.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.integration_notes || "(no notes)"} — score {s.symbolic_alignment_score}
          </li>
        ))}
        {strands.length === 0 && (
          <li className="list-group-item text-muted">No strands recorded.</li>
        )}
      </ul>
    </div>
  );
}
