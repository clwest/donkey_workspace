import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythflowHeatmapViewer() {
  const [data, setData] = useState([]);

  useEffect(() => {
    apiFetch("/metrics/mythflow-heatmap/")
      .then((res) => setData(res))
      .catch(() => setData([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Mythflow Heatmap</h5>
      <ul className="list-group">
        {data.map((d) => (
          <li key={d.title} className="list-group-item">
            {d.title}: {d.session_count}
          </li>
        ))}
        {data.length === 0 && (
          <li className="list-group-item text-muted">No heatmap data.</li>
        )}
      </ul>
    </div>
  );
}
