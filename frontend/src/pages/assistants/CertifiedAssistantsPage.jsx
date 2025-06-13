import { useEffect, useState } from "react";
import AssistantDashboardCard from "../../components/assistant/AssistantDashboardCard";
import apiFetch from "../../utils/apiClient";

export default function CertifiedAssistantsPage() {
  const [assistants, setAssistants] = useState([]);
  useEffect(() => {
    apiFetch("/assistants/?certified=true").then(setAssistants);
  }, []);
  return (
    <div className="container my-5">
      <h1 className="display-5 mb-4">🎖 Certified Assistants</h1>
      <div className="row g-4">
        {assistants.map((a) => (
          <div className="col-md-6 col-lg-4" key={a.id}>
            <AssistantDashboardCard assistant={a} />
          </div>
        ))}
      </div>
    </div>
  );
}
