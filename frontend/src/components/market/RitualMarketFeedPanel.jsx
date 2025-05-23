import { useEffect, useState } from "react";
import { fetchRitualMarketFeeds } from "../../api/agents";

export default function RitualMarketFeedPanel() {
  const [feeds, setFeeds] = useState([]);

  useEffect(() => {
    fetchRitualMarketFeeds()
      .then((res) => setFeeds(res.results || res))
      .catch(() => setFeeds([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Market Feed</h5>
      <ul className="list-group">
        {feeds.map((f) => (
          <li key={f.id} className="list-group-item">
            {f.ritual?.name || f.ritual} – {f.symbolic_price}
          </li>
        ))}
        {feeds.length === 0 && (
          <li className="list-group-item text-muted">No market data.</li>
        )}
      </ul>
    </div>
  );
}
