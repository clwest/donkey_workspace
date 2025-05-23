import { useEffect, useState } from "react";
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, LinearScale, Tooltip, Legend } from 'chart.js';
import apiFetch from "../../../utils/apiClient";

ChartJS.register(LineElement, PointElement, LinearScale, Tooltip, Legend);

export default function BeliefEvolutionDashboard({ assistantId }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${assistantId}/belief-history/`);
        setHistory(res.results || res);
      } catch (err) {
        console.error("Failed to load belief history", err);
        setHistory([]);
      }
    }
    load();
  }, [assistantId]);

  if (!history.length) return <div>No belief data.</div>;

  const labels = history.map(h => new Date(h.created_at).toLocaleDateString());
  const data = {
    labels,
    datasets: [
      {
        label: 'Alignment',
        data: history.map(h => h.codex_alignment_score || 0),
        borderColor: '#0d6efd',
        fill: false,
      }
    ]
  };
  const options = { scales: { y: { beginAtZero: true, max: 1 } }, plugins: { legend: { display: false } } };

  return (
    <div style={{ maxWidth: '400px' }}>
      <Line data={data} options={options} />
    </div>
  );
}
