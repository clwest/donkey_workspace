import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function StrategyChamberConsole() {
  const [chambers, setChambers] = useState([]);

  useEffect(() => {
    apiFetch("/strategy-chambers/")
      .then((res) => setChambers(res.results || res))
      .catch(() => setChambers([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Strategy Chambers</h5>
      <ul className="list-group">
        {chambers.map((c) => (
          <li key={c.id} className="list-group-item">
            {c.chamber_title}
          </li>
        ))}
        {chambers.length === 0 && (
          <li className="list-group-item text-muted">No chambers found.</li>
        )}
      </ul>
    </div>
  );
}
