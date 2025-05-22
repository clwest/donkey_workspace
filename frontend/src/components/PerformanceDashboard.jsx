import { useEffect, useState } from "react";

export default function PerformanceDashboard({ assistantId }) {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    fetch(`http://localhost:8000/api/metrics/performance/${assistantId}/`)
      .then((res) => res.json())
      .then((data) => setMetrics(data.metrics || []))
      .catch((e) => console.error("metrics", e));
  }, [assistantId]);

  return (
    <div className="p-2 border rounded">
      <h5>Performance Metrics</h5>
      <pre className="small bg-light p-2">
        {JSON.stringify(metrics, null, 2)}
      </pre>
    </div>
  );
}
