import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AssistantRefinementWizard from "../assistant/AssistantRefinementWizard";
import apiFetch from "@/utils/apiClient";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(LineElement, PointElement, LinearScale, Tooltip, Legend);

export default function DriftDiagnosisPanel({ slug, sessionId }) {
  const [data, setData] = useState(null);
  const [open, setOpen] = useState(false);
  const [showWizard, setShowWizard] = useState(false);

  useEffect(() => {
    if (!slug || !sessionId) return;
    apiFetch(`/assistants/${slug}/demo_session/${sessionId}/drift_diagnosis/`)
      .then(setData)
      .catch(() => {});
  }, [slug, sessionId]);

  useEffect(() => {
    if (data && data.diagnosis.length && !localStorage.getItem(`driftRefined-${slug}`)) {
      setShowWizard(true);
      localStorage.setItem(`driftRefined-${slug}`, "1");
    }
  }, [data, slug]);

  if (!data) return null;

  const chartData = {
    labels: data.fallback_series.map((_, i) => `Msg ${i + 1}`),
    datasets: [
      {
        label: "Fallback",
        data: data.fallback_series,
        borderColor: "#dc3545",
        fill: false,
      },
    ],
  };
  const options = { scales: { y: { beginAtZero: true, max: 1 } } };

  return (
    <div className="border rounded p-2 mt-3">
      <div
        role="button"
        className="d-flex justify-content-between"
        onClick={() => setOpen((v) => !v)}
      >
        <strong>Drift Diagnosis</strong>
        <span>{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div className="mt-2">
          <div className="mb-2">
            {data.diagnosis.map((d) => (
              <span key={d} className="badge bg-warning text-dark me-1">
                {d}
              </span>
            ))}
          </div>
          {data.most_missed_terms.length > 0 && (
            <div className="mb-2">
              <strong>Missed:</strong> {data.most_missed_terms.join(", ")}
            </div>
          )}
          <div className="mb-2">
            <Line data={chartData} options={options} height={80} />
          </div>
          <button
            className="btn btn-sm btn-primary"
            onClick={() => setShowWizard(true)}
          >
            Refine this Assistant
          </button>
        </div>
      )}
      <AssistantRefinementWizard
        slug={slug}
        sessionId={sessionId}
        show={showWizard}
        onClose={() => setShowWizard(false)}
      />
    </div>
  );
}
