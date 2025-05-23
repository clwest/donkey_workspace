import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function TokenMarketPanel() {
  const [listings, setListings] = useState([]);

  useEffect(() => {
    apiFetch("/belief-token-market/")
      .then((data) => setListings(data.results || data))
      .catch(() => {});
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Token Market</h5>
      <ul className="list-group">
        {listings.map((l) => (
          <li key={l.id} className="list-group-item">
            <strong>{l.token?.name || l.name}</strong>
            <span className="ms-2 text-muted small">{l.trade_volume}</span>
          </li>
        ))}
        {listings.length === 0 && (
          <li className="list-group-item text-muted">No tokens listed.</li>
        )}
      </ul>
    </div>
  );
}
