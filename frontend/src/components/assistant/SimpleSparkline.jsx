import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  Tooltip,
} from "chart.js";

ChartJS.register(LineElement, PointElement, LinearScale, Tooltip);

export default function SimpleSparkline({ data = [] }) {
  if (!data.length) return null;
  const labels = data.map((_, i) => i + 1);
  const chartData = {
    labels,
    datasets: [
      {
        data,
        borderColor: "#0d6efd",
        fill: false,
        tension: 0.3,
        pointRadius: 0,
      },
    ],
  };
  const options = {
    scales: { y: { display: false } },
    plugins: { legend: { display: false } },
  };
  return (
    <div style={{ width: "120px" }}>
      <Line data={chartData} options={options} />
    </div>
  );
}
