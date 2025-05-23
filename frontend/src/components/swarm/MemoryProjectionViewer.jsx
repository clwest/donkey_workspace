import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryProjectionViewer() {
  const [frames, setFrames] = useState([]);

  useEffect(() => {
    apiFetch("/memory-projection/")
      .then((res) => setFrames(res.results || res))
      .catch(() => setFrames([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Memory Projection Frames</h5>
      <ul className="list-group">
        {frames.map((f) => (
          <li key={f.id} className="list-group-item">
            {f.id}
          </li>
        ))}
        {frames.length === 0 && (
          <li className="list-group-item text-muted">No frames found.</li>
        )}
      </ul>
    </div>
  );
}
