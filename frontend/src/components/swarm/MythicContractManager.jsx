import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythicContractManager() {
  const [contracts, setContracts] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/mythic-contracts/");
        setContracts(res.results || res);
      } catch (err) {
        console.error("Failed to load contracts", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Mythic Contracts</h5>
      <ul className="list-group">
        {contracts.map((c) => (
          <li key={c.id} className="list-group-item">
            <strong>{c.title}</strong> – {c.contract_status}
          </li>
        ))}
        {contracts.length === 0 && (
          <li className="list-group-item text-muted">No contracts.</li>
        )}
      </ul>
    </div>
  );
}
