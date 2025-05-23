import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SignalArtifactTransmitter() {
  const [artifacts, setArtifacts] = useState([]);

  useEffect(() => {
    apiFetch("/signal-artifacts/")
      .then((res) => setArtifacts(res.results || res))
      .catch(() => setArtifacts([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Signal Artifacts</h5>
      <ul className="list-group">
        {artifacts.map((a) => (
          <li key={a.id} className="list-group-item">
            {a.symbolic_origin} – {a.receiver_scope}
          </li>
        ))}
        {artifacts.length === 0 && (
          <li className="list-group-item text-muted">No signal artifacts.</li>
        )}
      </ul>
    </div>
  );
}
