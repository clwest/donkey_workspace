import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function MemoryMoodChart({ moodCounts = {} }) {
  const labels = Object.keys(moodCounts);
  const dataValues = Object.values(moodCounts);

  const data = {
    labels,
    datasets: [
      {
        data: dataValues,
        backgroundColor: [
          '#4CAF50',
          '#2196F3',
          '#FFC107',
          '#E91E63',
          '#9C27B0',
          '#FF5722',
          '#607D8B',
          '#FF9800',
        ],
        borderColor: '#fff',
        borderWidth: 2,
      },
    ],
  };

  return (
    <div style={{ width: '250px', height: '250px' }}>
      <Pie data={data} options={{ plugins: { legend: { position: 'bottom' } } }} />
    </div>
  );
}
