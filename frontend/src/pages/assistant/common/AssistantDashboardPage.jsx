import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../../utils/apiClient";
import AssistantCard from "../../../components/assistant/AssistantCard";


export default function AssistantDashboardPage() {
  const [assistants, setAssistants] = useState([]);

  useEffect(() => {
    async function fetchAssistants() {
      try {
        const data = await apiFetch("/assistants/");
        setAssistants(data);
        if (Array.isArray(data) && data.length === 0) {
          toast.info("No assistants found. Launch one to get started.");
        }
      } catch (err) {
        console.error("Failed to fetch assistants:", err);
      }
    }
    fetchAssistants();
  }, []);

  return (
    <div className="container my-5">
      <h1 className="display-5 mb-4">🧑‍💼 Assistant Dashboard</h1>

      {assistants.length === 0 ? (
        <p>No assistants available. Launch one to begin.</p>
      ) : (
        <div className="row g-4">
          {assistants.map((assistant) => (
            <div className="col-md-6 col-lg-4" key={assistant.id}>
              <AssistantCard
                assistant={assistant}
                to={
                  assistant.current_project
                    ? `/assistants/projects/${assistant.current_project.id}`
                    : `/assistants/${assistant.slug}`
                }
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
