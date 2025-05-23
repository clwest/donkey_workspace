import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function SignalSourcesPage() {
  const [sources, setSources] = useState([]);

  useEffect(() => {
    async function fetchSources() {
      try {
        const data = await apiFetch(`/assistants/sources/`);
        setSources(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to load signal sources", err);
        setSources([]);
      }
    }
    fetchSources();
  }, []);

  return (
    <div className="container my-5">
      <h1 className="mb-4">📡 Signal Sources</h1>

      {sources.length === 0 ? (
        <p>No signal sources yet.</p>
      ) : (
        <ul className="list-group">
          {sources.map(source => (
            <li key={source.id} className="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{source.name}</strong><br />
                <small className="text-muted">{source.description}</small>
              </div>
              <span className="badge bg-primary rounded-pill">
                Priority: {source.priority}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}