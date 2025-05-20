import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, LinearScale, TimeScale, Tooltip, Legend } from 'chart.js';

ChartJS.register(LineElement, PointElement, LinearScale, TimeScale, Tooltip, Legend);

export default function DriftScoreChart({ logs = [] }) {
  if (!logs.length) return <div>No drift data.</div>;
  const labels = logs.map(l => new Date(l.created_at).toLocaleDateString());
  const data = {
    labels,
    datasets: [
      {
        label: 'Drift Score',
        data: logs.map(l => l.score),
        borderColor: '#dc3545',
        fill: false,
      },
    ],
  };
  const options = { scales: { y: { beginAtZero: true, max: 1 } } };
  return (
    <div style={{ maxWidth: '400px' }}>
      <Line data={data} options={options} />
    </div>
  );
}
