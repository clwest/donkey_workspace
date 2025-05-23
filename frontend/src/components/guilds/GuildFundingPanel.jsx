import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function GuildFundingPanel({ guildId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!guildId) return;
    apiFetch(`/guilds/${guildId}/funding/`)
      .then((res) => setData(res))
      .catch(() => setData(null));
  }, [guildId]);

  if (!data) return <div>Loading funding...</div>;

  return (
    <div className="my-3">
      <h5>Guild Funding</h5>
      <p>Symbolic Reserve: {data.symbolic_reserve}</p>
      <div className="mb-2">
        <strong>Proposed Allocations</strong>
        <pre style={{ whiteSpace: "pre-wrap" }}>
          {JSON.stringify(data.proposed_allocations, null, 2)}
        </pre>
      </div>
      <div className="mb-2">
        <strong>Votes</strong>
        <pre style={{ whiteSpace: "pre-wrap" }}>
          {JSON.stringify(data.contributor_votes, null, 2)}
        </pre>
      </div>
      <div>
        <strong>Approved Projects</strong>
        <pre style={{ whiteSpace: "pre-wrap" }}>
          {JSON.stringify(data.approved_projects, null, 2)}
        </pre>
      </div>
    </div>
  );
}
