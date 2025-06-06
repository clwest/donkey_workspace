import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function VocabularyProgressPanel({ assistantSlug }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (!assistantSlug) return;
    apiFetch(`/assistants/${assistantSlug}/glossary_stats/`)
      .then(setStats)
      .catch(() => setStats(null));
  }, [assistantSlug]);

  if (!stats) return <div>Loading vocabulary progress...</div>;

  const total =
    stats.reinforced + stats.acquired + stats.exposed + stats.unseen;

  return (
    <div className="card my-3">
      <div className="card-header">Vocabulary Progress</div>
      <div className="card-body">
        <p>{total} glossary terms total</p>
        <div className="progress" style={{ height: "1.5rem" }}>
          <div
            className="progress-bar bg-success"
            style={{ width: `${(stats.reinforced / total) * 100}%` }}
            title={`Reinforced: ${stats.reinforced}`}
          />
          <div
            className="progress-bar bg-info text-dark"
            style={{ width: `${(stats.acquired / total) * 100}%` }}
            title={`Acquired: ${stats.acquired}`}
          />
          <div
            className="progress-bar bg-warning text-dark"
            style={{ width: `${(stats.exposed / total) * 100}%` }}
            title={`Exposed: ${stats.exposed}`}
          />
          <div
            className="progress-bar bg-secondary"
            style={{ width: `${(stats.unseen / total) * 100}%` }}
            title={`Unseen: ${stats.unseen}`}
          />
        </div>
      </div>
    </div>
  );
}
