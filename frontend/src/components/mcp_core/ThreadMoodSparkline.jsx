import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, LinearScale, Tooltip } from 'chart.js';

ChartJS.register(LineElement, PointElement, LinearScale, Tooltip);

const MOOD_MAP = { neutral: 0, optimistic: 1, confident: 1, playful: 1, anxious: -1, frustrated: -2 };

function moodToValue(m) {
  return MOOD_MAP[m] ?? 0;
}

export default function ThreadMoodSparkline({ moods = [] }) {
  if (!moods.length) return null;
  const labels = moods.map(m => new Date(m.created_at).toLocaleDateString());
  const data = {
    labels,
    datasets: [
      {
        label: 'Mood',
        data: moods.map(m => moodToValue(m.mood)),
        borderColor: '#6c757d',
        fill: false,
        tension: 0.3,
        pointRadius: 2,
      },
    ],
  };
  const options = { scales: { y: { display: false, min: -2, max: 2 } }, plugins: { legend: { display: false } } };
  return (
    <div style={{ width: '120px' }}>
      <Line data={data} options={options} />
    </div>
  );
}
