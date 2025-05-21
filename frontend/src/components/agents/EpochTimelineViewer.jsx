import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function EpochTimelineViewer() {
  const [epochs, setEpochs] = useState([]);

  useEffect(() => {
    apiFetch("/agents/lore-epochs/")
      .then(setEpochs)
      .catch(() => setEpochs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Lore Epochs</h5>
      <ul className="list-group">
        {epochs.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.title}</strong>
            {e.closed && <span className="badge bg-secondary ms-2">closed</span>}
          </li>
        ))}
        {epochs.length === 0 && (
          <li className="list-group-item text-muted">No epochs found.</li>
        )}
      </ul>
    </div>
  );
}
