import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ForecastMarketPanel() {
  const [ledgers, setLedgers] = useState([]);

  useEffect(() => {
    apiFetch("/forecasting-ledgers/")
      .then((res) => setLedgers(res.results || res))
      .catch(() => setLedgers([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Forecasting Market Ledgers</h5>
      <ul className="list-group">
        {ledgers.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.market_scope} – {l.forecast_topic}
          </li>
        ))}
        {ledgers.length === 0 && (
          <li className="list-group-item text-muted">No ledger data.</li>
        )}
      </ul>
    </div>
  );
}
