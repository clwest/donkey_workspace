import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SwarmSeasonBanner() {
  const [season, setSeason] = useState(null);

  useEffect(() => {
    apiFetch("/agents/current-season/")
      .then((d) => setSeason(d.season))
      .catch(() => setSeason(null));
  }, []);

  if (!season) return null;

  return (
    <div className="alert alert-info text-center" data-testid="season-banner">
      Current Swarm Season: <strong>{season}</strong>
    </div>
  );
}
