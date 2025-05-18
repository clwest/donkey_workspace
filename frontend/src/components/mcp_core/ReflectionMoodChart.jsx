import { Pie, getElementsAtEvent } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useRef, useState } from 'react';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function ReflectionMoodChart({ reflections, onMoodSelect }) {
  const chartRef = useRef();
  const [selectedMood, setSelectedMood] = useState(null);

  const moodCounts = reflections.reduce((acc, reflection) => {
    const mood = reflection.mood || "Unknown";
    acc[mood] = (acc[mood] || 0) + 1;
    return acc;
  }, {});

  const labels = Object.keys(moodCounts);
  const counts = Object.values(moodCounts);

  const data = {
    labels,
    datasets: [
      {
        label: 'Reflections by Mood',
        data: counts,
        backgroundColor: [
          '#4CAF50', '#2196F3', '#FFC107', '#E91E63', '#9C27B0', '#FF5722', '#607D8B', '#FF9800'
        ],
        borderColor: '#ffffff',
        borderWidth: 2,
        hoverOffset: 15,
      },
    ],
  };

  const handleClick = (event) => {
    if (!chartRef.current) return;

    const elements = getElementsAtEvent(chartRef.current, event);
    if (elements.length > 0) {
      const index = elements[0].index;
      const moodLabel = labels[index];
      setSelectedMood(moodLabel);
      if (onMoodSelect) {
        onMoodSelect(moodLabel);
      }
    }
  };

  const handleReset = () => {
    setSelectedMood(null);
    if (onMoodSelect) {
      onMoodSelect(null);
    }
  };

  const customOptions = {
    maintainAspectRatio: false,
    onClick: handleClick,
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          color: "#333",
          font: {
            size: 14,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            return `${label}: ${value}`;
          }
        }
      }
    },
    animation: {
      animateRotate: true,
      animateScale: true,
    },
    elements: {
      arc: {
        borderWidth: 2,
        hoverBorderWidth: 3,
        backgroundColor: (ctx) => {
          const index = ctx.dataIndex;
          if (selectedMood) {
            return labels[index] === selectedMood
              ? ctx.dataset.backgroundColor[index]
              : "#ddd";  // dim others
          }
          return ctx.dataset.backgroundColor[index];
        },
        offset: (ctx) => {
          const index = ctx.dataIndex;
          return selectedMood && labels[index] === selectedMood ? 20 : 0;
        }
      }
    }
  };

  return (
    <div className="mb-4 text-center">
      <h5>Mood Overview</h5>

      {selectedMood && (
        <div className="my-3">
          <span className="badge bg-info text-dark" style={{ fontSize: "1rem", padding: "0.5rem 1rem" }}>
            Selected Mood: {selectedMood}
          </span>
          <button className="btn btn-sm btn-secondary ms-2" onClick={handleReset}>
            Reset Filter
          </button>
        </div>
      )}

      <div style={{ width: "400px", height: "400px", margin: "0 auto" }}>
        <Pie
          data={data}
          options={customOptions}
          ref={(el) => { chartRef.current = el?.chart; }}
        />
      </div>
    </div>
  );
}