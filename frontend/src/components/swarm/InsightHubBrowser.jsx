import { useEffect, useState } from "react";
import { fetchInsightHubs } from "../../api/agents";

export default function InsightHubBrowser() {
  const [hubs, setHubs] = useState([]);

  useEffect(() => {
    fetchInsightHubs()
      .then((d) => setHubs(d.results || d))
      .catch(() => setHubs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Insight Hubs</h5>
      <ul className="list-group">
        {hubs.map((h) => (
          <li key={h.id} className="list-group-item">
            {h.name}
          </li>
        ))}
        {hubs.length === 0 && (
          <li className="list-group-item text-muted">No hubs found.</li>
        )}
      </ul>
    </div>
  );
}
