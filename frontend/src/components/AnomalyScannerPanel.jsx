import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function AnomalyScannerPanel() {
  const [events, setEvents] = useState([]);
  useEffect(() => {
    apiFetch("/anomalies/").then(setEvents);
  }, []);
  return (
    <div className="p-2 border rounded">
      <h5>Symbolic Anomalies</h5>
      <ul>
        {events.map((e) => (
          <li key={e.id}>{e.anomaly_type} - {e.detected_by}</li>
        ))}
      </ul>
    </div>
  );
}
