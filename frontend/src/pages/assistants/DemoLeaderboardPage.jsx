import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function DemoLeaderboardPage() {
  useAuthGuard();
  const [rows, setRows] = useState(null);

  useEffect(() => {
    apiFetch("/assistants/demo_leaderboard/")
      .then((res) => setRows(Array.isArray(res) ? res : []))
      .catch(() => setRows([]));
  }, []);

  if (rows === null) {
    return <div className="container py-5">Loading...</div>;
  }

  const renderRatingTip = (dist) =>
    Object.entries(dist || {})
      .map(([k, v]) => `${k}: ${v}`)
      .join(" | ");

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between mb-3">
        <h2>Demo Leaderboard</h2>
        <Link to="/assistants-demos" className="btn btn-outline-secondary">
          ← Back to Demos
        </Link>
      </div>
      <div className="table-responsive">
        <table className="table table-sm table-bordered">
          <thead className="table-light">
            <tr>
              <th>Assistant</th>
              <th>Sessions</th>
              <th>Conversion</th>
              <th>Avg Score</th>
              <th>Avg Msgs</th>
              <th>Bounce</th>
              <th>Last Active</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.demo_slug}>
                <td>{row.label}</td>
                <td>{row.total_sessions}</td>
                <td>{(row.conversion_rate * 100).toFixed(1)}%</td>
                <td title={renderRatingTip(row.rating_distribution)}>
                  {row.avg_interaction_score.toFixed(2)}
                </td>
                <td>{row.avg_message_count.toFixed(1)}</td>
                <td>{(row.bounce_rate * 100).toFixed(1)}%</td>
                <td>
                  {row.latest_session_date
                    ? new Date(row.latest_session_date).toLocaleString()
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
