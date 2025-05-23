import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualRewardsPage() {
  const [rewards, setRewards] = useState([]);
  useEffect(() => {
    apiFetch("/ritual/rewards/").then((res) => setRewards(res.results || res));
  }, []);
  return (
    <div className="container mt-4">
      <h2>Ritual Rewards</h2>
      <pre>{JSON.stringify(rewards, null, 2)}</pre>
    </div>
  );
}
