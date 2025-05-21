import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AssistantReputationCard({ slug }) {
  const [rep, setRep] = useState(null);

  useEffect(() => {
    if (!slug) return;
    apiFetch(`/assistants/${slug}/reputation/`)
      .then((data) => setRep(data))
      .catch(() => {});
  }, [slug]);

  if (!rep) return null;

  return (
    <div className="card my-3">
      <div className="card-body">
        <h5 className="card-title">Reputation</h5>
        <p className="card-text">Score: {rep.reputation_score}</p>
        <p className="card-text small text-muted">
          Created: {rep.tokens_created} | Endorsed: {rep.tokens_endorsed} |
          Received: {rep.tokens_received}
        </p>
      </div>
    </div>
  );
}
