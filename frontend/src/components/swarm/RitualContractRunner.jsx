import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualContractRunner() {
  const [contracts, setContracts] = useState([]);

  useEffect(() => {
    apiFetch("/ritual-contracts/")
      .then((res) => setContracts(res.results || res))
      .catch(() => setContracts([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Contracts</h5>
      <ul className="list-group">
        {contracts.map((c) => (
          <li key={c.id} className="list-group-item">
            {c.initiator} – {c.cycle_active ? "active" : "inactive"}
          </li>
        ))}
        {contracts.length === 0 && (
          <li className="list-group-item text-muted">No contracts found.</li>
        )}
      </ul>
    </div>
  );
}
