import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function AssistantDemoPage() {
  const [assistants, setAssistants] = useState([]);

  useEffect(() => {
    fetch("/api/assistants/demos/")
      .then((res) => res.json())
      .then((data) => setAssistants(data))
      .catch((err) => console.error("Failed to fetch demo assistants:", err));
  }, []);

  return (
    <div className="container py-5">
      <h1 className="mb-4">🧪 AI Assistant Demos</h1>
      <div className="row">
        {assistants.map((assistant) => (
          <div key={assistant.id} className="col-md-4 mb-4">
            <div className="card h-100 shadow-sm border-0">
              <div className="card-body">
                <div className="d-flex align-items-center mb-3">
                  {assistant.avatar ? (
                    <img
                      src={assistant.avatar}
                      alt={assistant.name}
                      className="rounded-circle me-3"
                      style={{ width: "50px", height: "50px", objectFit: "cover" }}
                    />
                  ) : (
                    <div
                      className="rounded-circle bg-secondary me-3 d-flex justify-content-center align-items-center"
                      style={{ width: "50px", height: "50px", color: "white" }}
                    >
                      🤖
                    </div>
                  )}
                  <h5 className="mb-0">{assistant.name}</h5>
                </div>
                <p className="text-muted" style={{ fontSize: "0.9rem" }}>
                  {assistant.description || "No description provided."}
                </p>
                {assistant.specialty && (
                  <span className="badge bg-info text-dark">{assistant.specialty}</span>
                )}
              </div>
              <div className="card-footer bg-transparent border-0 text-end">
                <Link
                  to={`/assistants/${assistant.slug}`}
                  className="btn btn-outline-primary btn-sm"
                >
                  View Details
                </Link>
                <div>
                <Link to={`/assistants/${assistant.slug}/chat`} className="btn btn-outline-primary btn-sm mt-2">
                    💬 Chat
                </Link>
                </div>
              </div>
            </div>
          </div>
        ))}
        {assistants.length === 0 && (
          <p className="text-muted text-center">No demo assistants available yet.</p>
        )}
      </div>
    </div>
  );
}
