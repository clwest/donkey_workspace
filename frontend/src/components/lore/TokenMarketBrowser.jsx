import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function TokenMarketBrowser() {
  const [listings, setListings] = useState([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    apiFetch("/token-market/")
      .then((data) => setListings(data.results || data))
      .catch(() => {});
  }, []);

  const filtered = listings.filter((l) => {
    const q = filter.toLowerCase();
    return (
      l.token.name.toLowerCase().includes(q) ||
      (l.token.summary || "").toLowerCase().includes(q)
    );
  });

  return (
    <div className="my-3">
      <h5>Token Market</h5>
      <input
        className="form-control mb-2"
        placeholder="Filter by text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      <ul className="list-group">
        {filtered.map((l) => (
          <li key={l.id} className="list-group-item">
            <strong>{l.token.name}</strong>
            <span className="ms-2 text-muted small">{l.visibility}</span>
          </li>
        ))}
        {filtered.length === 0 && (
          <li className="list-group-item text-muted">No tokens found.</li>
        )}
      </ul>
    </div>
  );
}
