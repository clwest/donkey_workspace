import { useEffect, useState } from "react";
import PromptUsageLogTable from "./PromptUsageLogTable";
import LoadingSpinner from "../LoadingSpinner";
import apiFetch from "../../utils/apiClient";

export default function PromptUsageLogList({ promptSlug }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!promptSlug) return;

    async function fetchLogs() {
      try {
        const data = await apiFetch(`/prompts/${promptSlug}/usage-logs/`); // it's already parsed!
        console.log(data)
        setLogs(data); // 👈 works fine now
      } catch (err) {
        console.error("Error fetching usage logs:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchLogs();
  }, [promptSlug]);

  return (
    <div className="card p-3 shadow-sm">
      <h5 className="mb-3">📊 Usage Logs</h5>
      {loading ? (
        <LoadingSpinner />
      ) : logs.length === 0 ? (
        <p className="text-muted">No usage history yet.</p>
      ) : (
        <PromptUsageLogTable promptSlug={promptSlug} />
      )}
    </div>
  );
}
