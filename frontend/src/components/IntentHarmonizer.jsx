import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function IntentHarmonizer() {
  const [sessions, setSessions] = useState([]);
  useEffect(() => {
    apiFetch("/intent-harmony/").then(setSessions);
  }, []);

  return (
    <div className="p-2 border rounded">
      <h5>Intent Harmonization Sessions</h5>
      <ul>
        {sessions.map((s) => (
          <li key={s.id}>{s.symbolic_alignment_score} - {s.consensus_reached ? "Yes" : "No"}</li>
        ))}
      </ul>
    </div>
  );
}
