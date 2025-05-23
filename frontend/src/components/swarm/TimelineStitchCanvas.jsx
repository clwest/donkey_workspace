import { useEffect, useState } from "react";
import { fetchTimelineStitchLogs } from "../../api/agents";

export default function TimelineStitchCanvas() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchTimelineStitchLogs()
      .then((d) => setLogs(d.results || d))
      .catch(() => setLogs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Timeline Stitch Logs</h5>
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.stitching_method}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No stitch logs.</li>
        )}
      </ul>
    </div>
  );
}
