import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ConvergenceScorePanel({ assistantSlug, loreId }) {
  const [score, setScore] = useState(null);

  useEffect(() => {
    async function load() {
      if (!assistantSlug || !loreId) return;
      try {
        const data = await apiFetch(
          `/assistants/${assistantSlug}/lore/${loreId}/convergence/`,
        );
        setScore(data.score);
      } catch (err) {
        console.error("Failed to fetch convergence score", err);
      }
    }
    load();
  }, [assistantSlug, loreId]);

  if (score === null) return <div>Loading convergence...</div>;

  return (
    <div className="alert alert-info">Symbolic Convergence: {score}</div>
  );
}
