import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MissionConsensusPanel() {
  const [rounds, setRounds] = useState([]);

  useEffect(() => {
    apiFetch("/agents/mission-consensus/")
      .then((data) => setRounds(data.results || data))
      .catch(() => setRounds([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Mission Consensus Rounds</h5>
      <ul className="list-group">
        {rounds.map((r) => (
          <li key={r.id} className="list-group-item">
            {r.title}
          </li>
        ))}
        {rounds.length === 0 && (
          <li className="list-group-item text-muted">No consensus rounds.</li>
        )}
      </ul>
    </div>
  );
}
