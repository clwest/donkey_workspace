import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythflowOrchestrator() {
  const [plans, setPlans] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/mythflow-plans/");
        setPlans(res.results || res);
      } catch (err) {
        console.error("Failed to load plans", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Mythflow Plans</h5>
      <ul className="list-group">
        {plans.map((p) => (
          <li key={p.id} className="list-group-item">
            <strong>{p.title}</strong> – {p.mythflow_state}
          </li>
        ))}
        {plans.length === 0 && (
          <li className="list-group-item text-muted">No plans defined.</li>
        )}
      </ul>
    </div>
  );
}
