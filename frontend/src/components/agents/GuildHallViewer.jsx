import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function GuildHallViewer() {
  const [guilds, setGuilds] = useState([]);

  useEffect(() => {
    apiFetch("/agents/guilds/")
      .then(setGuilds)
      .catch((err) => console.error("Failed to load guilds", err));
  }, []);

  return (
    <div className="my-3">
      <h5>Assistant Guilds</h5>
      <div className="row">
        {guilds.map((g) => (
          <div key={g.id} className="col-md-4 mb-2">
            <div className="border rounded p-2 h-100">
              <h6 className="mb-1">{g.name}</h6>
              <p className="mb-1">{g.charter}</p>
              <p className="text-muted mb-0">
                Members: {g.members ? g.members.map((m) => m.name).join(", ") : ""}
              </p>
            </div>
          </div>
        ))}
        {guilds.length === 0 && (
          <p className="text-muted">No guilds found.</p>
        )}
      </div>
    </div>
  );
}
