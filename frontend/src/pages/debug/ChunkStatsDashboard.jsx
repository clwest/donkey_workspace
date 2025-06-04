import { useState } from "react";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from "chart.js";
import { fetchChunkStats } from "../../api/intel";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function ChunkStatsDashboard() {
  const [docId, setDocId] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const load = async () => {
    setError(null);
    try {
      const res = await fetchChunkStats({ document_id: docId });
      setData(res);
    } catch (err) {
      setError("Failed to load stats");
    }
  };

  const chartData = data
    ? {
        labels: Object.keys(data.distribution),
        datasets: [
          {
            label: "Chunks",
            data: Object.values(data.distribution),
            backgroundColor: "#0d6efd",
          },
        ],
      }
    : null;

  return (
    <div className="container my-4">
      <h3>Chunk Score Stats</h3>
      <div className="mb-3">
        <input
          className="form-control mb-2"
          placeholder="Document ID"
          value={docId}
          onChange={(e) => setDocId(e.target.value)}
        />
        <button className="btn btn-primary" onClick={load}>
          Load
        </button>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      {chartData && (
        <div style={{ maxWidth: "400px" }}>
          <Bar data={chartData} />
          <div className="mt-2 small">
            Glossary hits: {data.glossary_hits}/{data.chunk_total}
          </div>
        </div>
      )}
    </div>
  );
}
