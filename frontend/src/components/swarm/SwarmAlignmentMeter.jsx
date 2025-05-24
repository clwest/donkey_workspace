import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SwarmAlignmentMeter() {
  const [score, setScore] = useState(null);

  useEffect(() => {
    apiFetch("/metrics/swarm/alignment/")
      .then((res) => setScore(res.results ? res.results[0] : res[0] || res))
      .catch(() => setScore(null));
  }, []);

  return (
    <div className="my-3">
      <h5>Swarm Alignment Score</h5>
      {score ? (
        <p className="mb-0">Score: {score.score}</p>
      ) : (
        <p className="text-muted mb-0">No alignment data.</p>
      )}
    </div>
  );
}
