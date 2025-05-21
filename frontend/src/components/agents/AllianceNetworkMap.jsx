import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AllianceNetworkMap() {
  const [alliances, setAlliances] = useState([]);

  useEffect(() => {
    apiFetch("/agents/alliances/")
      .then(setAlliances)
      .catch((err) => console.error("Failed to load alliances", err));
  }, []);

  if (alliances.length === 0) {
    return <div>No alliances formed.</div>;
  }

  return (
    <div className="card mb-3">
      <div className="card-header">Alliance Network</div>
      <div className="card-body">
        <ul className="list-group">
          {alliances.map((a) => (
            <li key={a.id} className="list-group-item">
              {a.name}: {a.founding_guilds.map((g) => g.name).join(", ")}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
