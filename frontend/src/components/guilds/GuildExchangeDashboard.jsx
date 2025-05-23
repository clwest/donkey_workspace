import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function GuildExchangeDashboard({ guildId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!guildId) return;
    apiFetch(`/guilds/${guildId}/exchange/`)
      .then((res) => setData(res))
      .catch(() => setData(null));
  }, [guildId]);

  if (!data) return <div>Loading exchange...</div>;

  return (
    <div className="my-3">
      <h5>Guild Exchange</h5>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
