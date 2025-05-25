import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function PerformanceDashboard({ assistantId }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    apiFetch(`/execution-logs/`)
      .then((data) => setLogs(data))
      .catch((e) => console.error("logs", e));
  }, [assistantId]);

  return (
    <div className="p-2 border rounded">
      <h5>Execution Logs</h5>
      <pre className="small bg-light p-2">{JSON.stringify(logs, null, 2)}</pre>
    </div>
  );
}
