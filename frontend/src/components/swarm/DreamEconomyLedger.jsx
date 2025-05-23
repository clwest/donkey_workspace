import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DreamEconomyLedger() {
  const [foundations, setFoundations] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/dream-economy/");
        setFoundations(res.results || res);
      } catch (err) {
        console.error("Failed to load dream economy data", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Dream Economy Ledger</h5>
      <ul className="list-group">
        {foundations.map((f) => (
          <li key={f.id} className="list-group-item">
            <strong>{f.economy_scope}</strong> – rate {f.legacy_conversion_rate}
          </li>
        ))}
        {foundations.length === 0 && (
          <li className="list-group-item text-muted">No dream economy configured.</li>
        )}
      </ul>
    </div>
  );
}
