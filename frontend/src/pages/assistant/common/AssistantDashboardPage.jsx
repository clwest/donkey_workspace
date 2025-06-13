import { useEffect, useState, useRef } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../../utils/apiClient";
import AssistantDashboardCard from "../../../components/assistant/AssistantDashboardCard";


export default function AssistantDashboardPage() {
  const [assistants, setAssistants] = useState([]);
  const [paused, setPaused] = useState(false);
  const lastRef = useRef(0);

  useEffect(() => {
    async function fetchAssistants() {
      if (Date.now() - lastRef.current < 1000) return;
      lastRef.current = Date.now();
      try {
        const data = await apiFetch("/assistants/");
        setAssistants(data);
        if (Array.isArray(data) && data.length === 0) {
          toast.info("No assistants found. Launch one to get started.");
        }
      } catch (err) {
        if (err.status === 429) {
          setPaused(true);
        }
        console.error("Failed to fetch assistants:", err);
      }
    }
    fetchAssistants();
  }, []);

  return (
    <div className="container my-5" id="dashboard-page">
      <h1 className="display-5 mb-4">🧑‍💼 Assistant Dashboard</h1>
      {paused && (
        <div className="alert alert-warning">Paused due to rate limit</div>
      )}

      {assistants.length === 0 ? (
        <p>No assistants available. Launch one to begin.</p>
      ) : (
        <div className="row g-4">
          {assistants.map((assistant) => (
            <div className="col-md-6 col-lg-4" key={assistant.id}>
              <AssistantDashboardCard assistant={assistant} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
