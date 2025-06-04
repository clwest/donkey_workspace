import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import apiFetch from "@/utils/apiClient";

import { cleanRecentMemories, cleanStaleProjects } from "../../api/assistants";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function AssistantDiagnosticsPanel({ slug, onRefresh }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    apiFetch(`/assistants/${slug}/diagnostics/`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [slug, refreshKey]);

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


  const cooldown = () =>
    setTimeout(() => {
      setAction(null);
    }, 5000);

  const handleReflect = async () => {
    if (action) return;
    setAction("reflect");
    try {
      await apiFetch(`/assistants/${slug}/reflect_now/`, { method: "POST" });
      toast.success("Reflection complete");
      setRefreshKey((k) => k + 1);
    } catch {
      toast.error("Failed to run reflection");
    } finally {
      cooldown();
    }
  };

  const handleFixContext = async () => {
    if (action) return;
    setAction("context");
    try {
      const res = await apiFetch(`/assistants/${slug}/fix_context/`, {
        method: "POST",
      });
      toast.info(`Linked ${res.updated} memories`);
      setRefreshKey((k) => k + 1);
    } catch {
      toast.error("Failed to fix context");
    } finally {
      cooldown();
    }
  };

  const handleSyncAnchors = async () => {
    if (action) return;
    setAction("anchors");
    try {
      const res = await apiFetch(`/assistants/${slug}/retag_glossary_chunks/`, {
        method: "POST",
      });
      toast.success(`Retagged ${res.matched_total} chunks`);
      setRefreshKey((k) => k + 1);
    } catch {
      toast.error("Failed to sync glossary anchors");
    } finally {
      cooldown();

    }
  };

  const handleCleanMemories = async () => {
    if (action) return;
    if (!window.confirm("Remove weak memories?")) return;
    setAction("memories");
    try {
      await cleanRecentMemories(slug);
      toast.success("Weak memories cleaned");
      setRefreshKey((k) => k + 1);
      onRefresh && onRefresh();
    } catch {
      toast.error("Failed to clean memories");
    } finally {
      cooldown();
    }
  };

  const handleCleanProjects = async () => {
    if (action) return;
    if (!window.confirm("Remove stale projects?")) return;
    setAction("projects");
    try {
      await cleanStaleProjects(slug);
      toast.success("Stale projects cleaned");
      setRefreshKey((k) => k + 1);
      onRefresh && onRefresh();
    } catch {
      toast.error("Failed to clean projects");
    } finally {
      cooldown();
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

        <button
          className="btn btn-sm btn-outline-primary me-1"
          onClick={handleReflect}
          disabled={!!action}
        >
          {action === "reflect" ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" />
              Running...
            </>
          ) : (
            "🧠 Re-run Reflection"
          )}
        </button>
        <button
          className="btn btn-sm btn-outline-secondary me-1"
          onClick={handleFixContext}
          disabled={!!action}
        >
          {action === "context" ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" />
              Linking...
            </>
          ) : (
            "🔧 Fix Context"
          )}
        </button>
        <button
          className="btn btn-sm btn-outline-success"
          onClick={handleSyncAnchors}
          disabled={!!action}
        >
          {action === "anchors" ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" />
              Syncing...
            </>
          ) : (
            "📚 Sync Glossary Anchors"
          )}

        </button>
        <button
          className="btn btn-sm btn-outline-danger ms-1"
          onClick={handleCleanMemories}
          disabled={!!action}
        >
          {action === "memories" ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" />
              Cleaning...
            </>
          ) : (
            "🧹 Clean Weak Memories"
          )}
        </button>
        <button
          className="btn btn-sm btn-outline-danger ms-1"
          onClick={handleCleanProjects}
          disabled={!!action}
        >
          {action === "projects" ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" />
              Removing...
            </>
          ) : (
            "🗑️ Clear Stale Projects"
          )}
        </button>
      </div>
    </div>
  );
}
