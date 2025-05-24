import { useEffect, useState } from "react";
import { fetchAssistantThoughtLog } from "../../api/agents";
import ThoughtLogCard from "./thoughts/ThoughtLogCard";

export default function AssistantThoughtStream({ assistantId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!assistantId) return;
    setLoading(true);
    fetchAssistantThoughtLog(assistantId)
      .then((res) => setLogs(res.results || res))
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, [assistantId]);

  return (
    <div className="p-2 border rounded" style={{ maxHeight: "400px", overflowY: "auto" }}>
      <h5>Thought Stream</h5>
      {loading && <div>Loading thoughts...</div>}
      {logs.length === 0 && !loading && (
        <div className="text-muted">No thoughts logged.</div>
      )}
      {logs.map((log) => (
        <ThoughtLogCard key={log.id} thought={log} />
      ))}
    </div>
  );
}
