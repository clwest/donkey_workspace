import { useEffect, useState } from "react";  
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function ReflectionsPage() {
  const [assistants, setAssistants] = useState([]);

  useEffect(() => {
    async function fetchAssistants() {
      try {
        const res = await apiFetch("/assistants/");
        setAssistants(res);
      } catch (err) {
        console.error("Failed to fetch assistants", err);
      }
    }

    fetchAssistants();
  }, []);

  return (
    <div className="container my-5">
      <h1 className="mb-4">🪞 Assistant Reflections</h1>
      <p className="text-muted mb-4">
        Review and trigger reflections from memory and project activities.
      </p>

      <div className="row">
        {assistants.map((a) => (
          <div key={a.slug} className="col-md-4 mb-4">
            <div className="card h-100 shadow-sm">
              <div className="card-body">
                <h5 className="card-title">{a.name}</h5>
                <p className="card-text text-muted">{a.description}</p>
                <Link to={`/assistants/${a.slug}/reflect`} className="btn btn-outline-primary w-100">
                  Reflect Now
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      <Link to="/projects" className="btn btn-outline-secondary mt-4">
        🔙 Back to Projects
      </Link>
    </div>
  );
}