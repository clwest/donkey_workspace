import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function DemoInsightsDashboard() {
  useAuthGuard();
  const [overview, setOverview] = useState(null);
  const [demos, setDemos] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/demo_usage/overview/")
      .then(setOverview)
      .catch(() => setOverview(null));
    apiFetch("/assistants/demos/")
      .then((res) => setDemos(Array.isArray(res) ? res : []))
      .catch(() => setDemos([]));
  }, []);

  if (!overview) {
    return <div className="container py-5">Loading...</div>;
  }

  const starterLabels = overview.top_starters.map((s) => s.prompt);
  const barData = {
    labels: starterLabels,
    datasets: [
      {
        label: "Uses",
        data: overview.top_starters.map((s) => s.count),
        backgroundColor: "#0d6efd",
      },
    ],
  };

  const conversionClass =
    overview.conversion_rate < 0.1 ? "border-danger text-danger" : "border-success";

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between mb-3">
        <h2>Demo Usage Insights</h2>
        <div>
          <Link to="/assistants/demos/feedback" className="btn btn-primary me-2">
            Feedback Explorer
          </Link>
          <Link to="/assistants-demos" className="btn btn-outline-secondary">
            ← Back to Demos
          </Link>
        </div>
      </div>
      <div className="row mb-4 g-3">
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h6>Total Sessions</h6>
              <div className="display-6">{overview.total_sessions}</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className={`card text-center ${conversionClass}`}>\
            <div className="card-body">
              <h6>Conversion Rate</h6>
              <div className="display-6">
                {(overview.conversion_rate * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h6>Avg Session Length</h6>
              <div className="display-6">
                {overview.avg_session_length.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h6>Bounce Rate</h6>
              <div className="display-6">
                {(overview.bounce_rate * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="mb-5" style={{ maxWidth: "500px" }}>
        <Bar data={barData} />
      </div>
      <div className="table-responsive">
        <table className="table table-sm table-bordered">
          <thead className="table-light">
            <tr>
              <th>Demo</th>
              <th>Sessions</th>
              <th>Avg Msgs</th>
              <th>Conversion</th>
              <th>Bounce</th>
              <th>Top Starter</th>
            </tr>
          </thead>
          <tbody>
            {demos.map((demo) => (
              <tr key={demo.id}>
                <td>{demo.name}</td>
                <td>{demo.metrics.total_sessions || 0}</td>
                <td>{(demo.metrics.avg_messages || 0).toFixed(2)}</td>
                <td>
                  {((demo.metrics.conversion_rate || 0) * 100).toFixed(1)}%
                </td>
                <td>
                  {((demo.metrics.bounce_rate || 0) * 100).toFixed(1)}%
                </td>
                <td>{demo.metrics.most_common_starter || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
