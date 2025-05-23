import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function NarrativePressureGauge({ sessionId }) {
  const [pressure, setPressure] = useState(null);

  useEffect(() => {
    if (!sessionId) return;
    apiFetch("/narrative-pressure/", { params: { session_id: sessionId } })
      .then((res) => setPressure(res))
      .catch(() => setPressure(null));
  }, [sessionId]);

  if (!pressure) {
    return <div className="my-3">No pressure data.</div>;
  }
  return (
    <div className="my-3">
      <h5>Narrative Pressure</h5>
      <pre>{JSON.stringify(pressure)}</pre>
    </div>
  );
}
