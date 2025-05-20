import { Scatter } from 'react-chartjs-2';
import { Chart as ChartJS, PointElement, LinearScale, Tooltip, Legend } from 'chart.js';
import { useMemo } from 'react';

ChartJS.register(PointElement, LinearScale, Tooltip, Legend);

const MOOD_COLORS = {
  curious: '#0d6efd',
  thoughtful: '#6610f2',
  playful: '#fd7e14',
  urgent: '#dc3545',
  focused: '#198754',
};

export default function MemoryVisualizer({ memories = [] }) {
  const data = useMemo(() => {
    return {
      datasets: [
        {
          label: 'Memories',
          data: memories.map((m, idx) => ({
            x: new Date(m.created_at).getTime(),
            y: 0,
            summary: m.summary,
            mood: m.mood,
          })),
          pointBackgroundColor: memories.map(m => MOOD_COLORS[m.mood] || '#6c757d'),
          pointBorderColor: '#fff',
          pointRadius: 6,
        },
      ],
    };
  }, [memories]);

  const options = {
    scales: {
      x: {
        type: 'linear',
        ticks: {
          callback: value => new Date(value).toLocaleDateString(),
        },
      },
      y: { display: false },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: ctx => ctx.raw.summary || '(no summary)',
        },
      },
      legend: { display: false },
    },
  };

  if (!memories.length) return <div>No memory data.</div>;

  return (
    <div className="mb-4">
      <Scatter data={data} options={options} />
    </div>
  );
}
