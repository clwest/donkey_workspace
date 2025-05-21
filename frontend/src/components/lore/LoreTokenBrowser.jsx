import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LoreTokenBrowser() {
  const [tokens, setTokens] = useState([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    apiFetch("/lore-tokens/")
      .then((data) => setTokens(data.results || data))
      .catch(() => {});
  }, []);

  const filtered = tokens.filter((t) => {
    const q = query.toLowerCase();
    return (
      t.name.toLowerCase().includes(q) ||
      (t.summary || "").toLowerCase().includes(q) ||
      ((t.symbolic_tags?.tags || []).join(" ").toLowerCase().includes(q))
    );
  });

  return (
    <div className="my-3">
      <h5>Lore Tokens</h5>
      <input
        className="form-control mb-2"
        placeholder="Filter by text or tag"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <ul className="list-group">
        {filtered.map((t) => (
          <li key={t.id} className="list-group-item">
            <div>
              <strong>{t.name}</strong>
            </div>
            <div className="small text-muted">
              {(t.symbolic_tags?.tags || []).join(", ")}
            </div>
          </li>
        ))}
        {filtered.length === 0 && (
          <li className="list-group-item text-muted">No tokens found.</li>
        )}
      </ul>
    </div>
  );
}
