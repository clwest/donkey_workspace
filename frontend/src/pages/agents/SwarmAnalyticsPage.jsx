import { useEffect, useState } from "react";
import { Line, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import apiFetch from "../../utils/apiClient";

ChartJS.register(LineElement, PointElement, LinearScale, TimeScale, ArcElement, Tooltip, Legend);

export default function SwarmAnalyticsPage() {
  const [report, setReport] = useState(null);
  const [clusters, setClusters] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [reason, setReason] = useState("");

  useEffect(() => {
    apiFetch("/agents/swarm-temporal-report/")
      .then(setReport)
      .catch((err) => console.error("Failed to load report", err));
    apiFetch("/agents/clusters/")
      .then(setClusters)
      .catch((err) => console.error("Failed to load clusters", err));
  }, []);

  if (!report) return <div className="container py-5">Loading...</div>;

  const timelineLabels = Object.keys(report.timeline || {});
  const lineData = {
    labels: timelineLabels,
    datasets: [
      {
        label: "Active Agents",
        data: Object.values(report.timeline || {}),
        borderColor: "#0d6efd",
        fill: false,
      },
    ],
  };

  const pieData = {
    labels: clusters.map((c) => c.name),
    datasets: [
      {
        data: clusters.map((c) => c.agents.length),
        backgroundColor: [
          "#4CAF50",
          "#FFC107",
          "#2196F3",
          "#E91E63",
          "#9C27B0",
        ],
      },
    ],
  };

  return (
    <div className="container py-4">
      <h1 className="mb-4">Swarm Analytics</h1>
      <div className="row mb-4">
        <div className="col-md-6">
          <Line data={lineData} />
        </div>
        <div className="col-md-6">
          <Pie data={pieData} />
        </div>
      </div>
      <div className="mb-4">
        <h5>Forecast</h5>
        <p>{report.forecast}</p>
      </div>
      <button className="btn btn-danger" onClick={() => setShowModal(true)}>
        Retire Agents
      </button>
      {showModal && (
        <div className="modal show d-block" tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Retire Agents</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="mb-3">
                  <label className="form-label">Reason</label>
                  <input
                    className="form-control"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button
                  className="btn btn-danger"
                  onClick={() => {
                    apiFetch("/agents/retire/", {
                      method: "POST",
                      body: { reason },
                    }).finally(() => setShowModal(false));
                  }}
                >
                  Retire
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
