import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import { fetchAgents } from "../../api/agents";


export default function SwarmMemoryViewer() {
  const [entries, setEntries] = useState([]);
  const [tag, setTag] = useState("");
  const [assistant, setAssistant] = useState("");
  const [assistants, setAssistants] = useState([]);
  const [tokens, setTokens] = useState([]);

  useEffect(() => {
    fetchAgents()
      .then(setAssistants)
      .catch(() => {});
    apiFetch("/lore-tokens/?limit=5")
      .then((d) => setTokens(d.results || d))
      .catch(() => setTokens([]));
  }, []);

  useEffect(() => {
    let url = "/agents/swarm-memory/";
    const params = [];
    if (tag) params.push(`tag=${encodeURIComponent(tag)}`);
    if (assistant) params.push(`assistant=${assistant}`);
    if (params.length) url += `?${params.join("&")}`;
    apiFetch(url)
      .then((d) => setEntries(d.results || d))
      .catch(() => setEntries([]));
  }, [tag, assistant]);

  return (
    <div className="my-3">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <h5 className="mb-0">Swarm Memory</h5>
        <Link to="/swarm/timeline" className="btn btn-sm btn-outline-secondary">
          View in Timeline
        </Link>
      </div>
      <div className="row mb-2 g-2">
        <div className="col">
          <input
            type="text"
            className="form-control"
            placeholder="Filter by tag"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
          />
        </div>
        <div className="col">
          <select
            className="form-select"
            value={assistant}
            onChange={(e) => setAssistant(e.target.value)}
          >
            <option value="">All Assistants</option>
            {assistants.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <ul className="list-unstyled">
        {entries.map((m) => (
          <li key={m.id} className="mb-2">
            <strong>{m.title}</strong> - {m.origin}
          </li>
        ))}
        {entries.length === 0 && (
          <li className="text-muted">No swarm memory found.</li>
        )}
      </ul>
      <h6 className="mt-4">Recent Token Summaries</h6>
      <ul className="list-group">
        {tokens.map((t) => (
          <li key={t.id} className="list-group-item small">
            {t.summary}
          </li>
        ))}
        {tokens.length === 0 && (
          <li className="list-group-item text-muted">No tokens found.</li>
        )}
      </ul>
    </div>
  );

}
