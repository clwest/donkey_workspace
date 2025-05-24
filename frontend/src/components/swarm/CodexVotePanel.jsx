import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CodexVotePanel() {
  const [votes, setVotes] = useState([]);

  useEffect(() => {
    apiFetch("/metrics/codex/vote/")
      .then((res) => setVotes(res.results || res))
      .catch(() => setVotes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Codex Clause Votes</h5>
      <ul className="list-group">
        {votes.map((v) => (
          <li key={v.id} className="list-group-item">
            {v.clause_id} – {v.vote_choice}
          </li>
        ))}
        {votes.length === 0 && (
          <li className="list-group-item text-muted">No votes yet.</li>
        )}
      </ul>
    </div>
  );
}
