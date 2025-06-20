import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function SignalCatchesPage() {
  const [catches, setCatches] = useState([]);

  useEffect(() => {
    async function fetchCatches() {
      const data = await apiFetch("/assistants/signals/");
      setCatches(data);
    }
    fetchCatches();
  }, []);

  return (
    <div className="container my-5">
      <h1 className="mb-4">🛰️ Caught Signals</h1>

      {catches.length === 0 ? (
        <p>No signals captured yet.</p>
      ) : (
        <ul className="list-group">
          {catches.map(signal => (
            <li key={signal.id} className="list-group-item">
              <strong>{signal.source_name || "Unknown Source"}</strong>: {signal.content}
              <br />
              <small className="text-muted">Created at {new Date(signal.created_at).toLocaleString()}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}