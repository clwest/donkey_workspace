import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SymbolicFuturesDashboard() {
  const [contracts, setContracts] = useState([]);

  useEffect(() => {
    apiFetch("/future-contracts/")
      .then((res) => setContracts(res.results || res))
      .catch(() => setContracts([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Symbolic Future Contracts</h5>
      <ul className="list-group">
        {contracts.map((c) => (
          <li key={c.id} className="list-group-item">
            {c.title} – {c.future_event_description}
          </li>
        ))}
        {contracts.length === 0 && (
          <li className="list-group-item text-muted">No contracts.</li>
        )}
      </ul>
    </div>
  );
}
