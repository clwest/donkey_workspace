import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SymbolExchangeTerminal() {
  const [exchanges, setExchanges] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/symbol-exchange/");
        setExchanges(res.results || res);
      } catch (err) {
        console.error("Failed to load exchanges", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Role Symbol Exchange</h5>
      <ul className="list-group">
        {exchanges.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.archetype_role}</strong> – {e.liquidity_available}
          </li>
        ))}
        {exchanges.length === 0 && (
          <li className="list-group-item text-muted">No exchange data.</li>
        )}
      </ul>
    </div>
  );
}
