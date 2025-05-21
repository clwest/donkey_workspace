import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RetconReviewPanel() {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/retcon-requests/");
        setRequests(res || []);
      } catch (err) {
        console.error("Failed to load retcon requests", err);
      }
    }
    load();
  }, []);

  return (
    <div>
      <h3>Retcon Requests</h3>
      <ul className="list-group">
        {requests.map((r) => (
          <li key={r.id} className="list-group-item">
            <p className="mb-1">
              <strong>{r.proposed_rewrite.slice(0, 80)}</strong>
            </p>
            <small className="text-muted">Justification: {r.justification}</small>
          </li>
        ))}
      </ul>
    </div>
  );
}
