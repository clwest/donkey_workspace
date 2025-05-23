import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LiquidityPoolConsole() {
  const [pools, setPools] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/dream-pools/");
        setPools(res.results || res);
      } catch (err) {
        console.error("Failed to load pools", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Dream Liquidity Pools</h5>
      <ul className="list-group">
        {pools.map((p) => (
          <li key={p.id} className="list-group-item">
            <strong>{p.pool_name}</strong>
          </li>
        ))}
        {pools.length === 0 && (
          <li className="list-group-item text-muted">No liquidity pools.</li>
        )}
      </ul>
    </div>
  );
}
