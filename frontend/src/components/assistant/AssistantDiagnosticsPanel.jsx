import { useEffect, useState } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import apiFetch from "@/utils/apiClient";
import { toast } from "react-toastify";
import { cleanRecentMemories, cleanStaleProjects } from "../../api/assistants";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function AssistantDiagnosticsPanel({ slug }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    apiFetch(`/assistants/${slug}/diagnostics/`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <div>Loading diagnostics...</div>;
  if (!data) return <div className="text-muted">No diagnostics available.</div>;

  const chartData = {
    labels: ["High", "Medium", "Low"],
    datasets: [
      {
        data: [
          data.chunk_score_distribution.high,
          data.chunk_score_distribution.medium,
          data.chunk_score_distribution.low,
        ],
        backgroundColor: ["#0d6efd", "#ffc107", "#dc3545"],
        borderColor: "#fff",
        borderWidth: 1,
      },
    ],
  };

  const handleCleanMemories = async () => {
    try {
      await cleanRecentMemories(slug);
      toast.success("Weak memories purged");
    } catch {
      toast.error("Cleanup failed");
    }
  };

  const handleCleanProjects = async () => {
    try {
      await cleanStaleProjects(slug);
      toast.success("Stale projects removed");
    } catch {
      toast.error("Project cleanup failed");
    }
  };

  return (
    <div className="p-2 border rounded mb-3">
      <h5 className="mb-3">Assistant Diagnostics</h5>
      <ul className="list-unstyled small mb-3">
        <li>✅ Memory context: Context ID: {data.context_id}</li>
        <li>🧠 Reflection logs: {data.reflections_total} reflections</li>
        <li>🔗 Orphaned memories: {data.orphaned_memory_count}</li>
        <li>
          📚 Glossary anchors: {data.anchors_total} total / {" "}
          {data.anchors_with_matches} matched
        </li>
      </ul>
      <div style={{ width: "250px", height: "250px" }}>
        <Pie data={chartData} options={{ plugins: { legend: { position: "bottom" } } }} />
      </div>
      <div className="mt-2">
        <button className="btn btn-sm btn-outline-primary me-1">🧠 Re-run Reflection</button>
        <button className="btn btn-sm btn-outline-secondary me-1">🔧 Fix Context</button>
        <button className="btn btn-sm btn-outline-success me-1">📚 Sync Glossary Anchors</button>
        <button className="btn btn-sm btn-outline-danger me-1" onClick={handleCleanMemories}>
          🧹 Clean Recent Memories
        </button>
        <button className="btn btn-sm btn-outline-danger" onClick={handleCleanProjects}>
          🗑 Clear Stale Projects
        </button>
      </div>
    </div>
  );
}
