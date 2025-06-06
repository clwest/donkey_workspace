import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function VocabularyProgressPanel({ assistantId }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (!assistantId) return;
    apiFetch(`/assistants/${assistantId}/anchor_health/`)
      .then((res) => {
        const stageCounts = { reinforced: 0, acquired: 0, exposed: 0, unseen: 0 };
        (res.results || res).forEach((a) => {
          stageCounts[a.acquisition_stage || "unseen"]++;
        });
        setStats(stageCounts);
      })
      .catch(() => setStats(null));
  }, [assistantId]);

  if (!stats) return <div>Loading vocabulary progress...</div>;

  const total =
    stats.reinforced + stats.acquired + stats.exposed + stats.unseen;

  return (
    <div className="card my-3">
      <div className="card-header">Vocabulary Progress</div>
      <div className="card-body">
        <p>{total} glossary terms total</p>
        <ul>
          <li>Reinforced: {stats.reinforced}</li>
          <li>Acquired: {stats.acquired}</li>
          <li>Exposed: {stats.exposed}</li>
          <li>Unseen: {stats.unseen}</li>
        </ul>
      </div>
    </div>
  );
}
