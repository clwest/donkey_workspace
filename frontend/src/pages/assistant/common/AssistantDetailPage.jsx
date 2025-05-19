import { useEffect, useState } from "react";
import { useParams, Link, useLocation } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import PrimaryStar from "../../../components/assistant/PrimaryStar";
import { toast } from "react-toastify";
import "./styles/AssistantDetail.css"

export default function AssistantDetailPage() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const [showTools, setShowTools] = useState(false);
  const threadId = query.get("thread");
  const projectId = query.get("project");
  const memoryId = query.get("memory");
  const objectiveId = query.get("objective");

  useEffect(() => {
    async function fetchAssistant() {
      try {
        const data = await apiFetch(`/assistants/${slug}/`);
        setAssistant(data);
        
      } catch (err) {
        console.error("Error fetching assistant:", err);
      }
    }
    fetchAssistant();
    
  }, [slug]);

  useEffect(() => {
    if (threadId) {
      console.log("📍 Would fetch thread:", threadId);
      // TODO: fetch thread data or display something visually
    }
    if (memoryId) {
      toast.success("Assistant created and linked to memory!");
      setTimeout(() => {
        document.getElementById(`memory-${memoryId}`)?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    }
    if (objectiveId) {
      toast.info("Linked objective ready!");
      setTimeout(() => {
        document.getElementById(`objective-${objectiveId}`)?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    }
  }, [threadId, memoryId, objectiveId]);

  if (!assistant) return <div className="container my-5">Loading assistant...</div>;

  return (
    <div className="container my-5">
      <h1 className="display-4">
        {assistant.name}
        <PrimaryStar isPrimary={assistant.is_primary} />
      </h1>
      <p className="text-muted">Assistant Details Page</p>

      <div className="mb-4">
        <p><strong>Slug:</strong> {assistant.slug}</p>
        <p><strong>Description:</strong> {assistant.description || "No description yet."}</p>
        <p><strong>Specialty:</strong> {assistant.specialty || "N/A"}</p>
        <p><strong>Status:</strong> {assistant.is_active ? "Active" : "Inactive"}</p>
        <p><strong>Created:</strong> {new Date(assistant.created_at).toLocaleString()}</p>
      </div>

      {assistant.current_project ? (
        <div className="alert alert-info">Assigned Project: {assistant.current_project.title} ({assistant.current_project.objective_count} objectives)</div>
      ) : (
        <button
          className="btn btn-outline-secondary mb-3"
          onClick={async () => {
            try {
              const projects = await apiFetch(`/assistants/${slug}/projects/`);
              const id = prompt("Assign project by ID", projects[0]?.id || "");
              if (id) {
                await apiFetch(`/assistants/${slug}/assign_project/`, {
                  method: "POST",
                  body: { project_id: id },
                });
                const data = await apiFetch(`/assistants/${slug}/`);
                setAssistant(data);
              }
            } catch (err) {
              alert("Failed to assign project");
            }
          }}
        >
          Assign Project
        </button>
      )}

      <div className="d-flex flex-wrap gap-3 mb-4">
        <Link to={`/assistants/${slug}/chat`} className="btn btn-dark">💬 Chat</Link>
        <Link to={`/assistants/${slug}/thoughts`} className="btn btn-outline-primary">🧠 Thought Log</Link>
        <Link to={`/assistants/${slug}/projects`} className="btn btn-outline-success">📂 Projects</Link>
        <Link to={`/assistants/${slug}/memories`} className="btn btn-outline-warning">📘 Memory</Link>
        <Link to={`/assistants/${slug}/reflect`} className="btn btn-outline-info">🔍 Reflections</Link>
        <Link to={`/assistants/${slug}/sessions`} className="btn btn-outline-secondary">
        💬 Sessions
      </Link>
        <Link to={`/assistants/${assistant.slug}/dashboard`} className="btn btn-outline-primary">
          🧠 View Dashboard
        </Link>

      </div>

      <hr />
      {assistant.documents?.length > 0 && (
        <>
          <h5 className="mt-4">📄 Linked Documents</h5>
          <ul className="list-group mb-3">
            {assistant.documents.map((doc) => (
              <li key={doc.id} className="list-group-item">
                <Link to={`/intel/documents/${doc.id}`}>{doc.title}</Link>
              </li>
            ))}
          </ul>
        </>
      )}

      {assistant.projects?.length > 0 && (
        <>
          <h5 className="mt-4">📂 Linked Projects</h5>
          <ul className="list-group mb-3">
          {assistant.projects.map((project) => (
            <li key={project.id} id={`project-${project.id}`} className="list-group-item">
              <Link to={`/assistants/projects/${project.id}`}>{project.title}</Link>
              {project.objectives?.length > 0 && (
                <ul className="mt-2 ms-3">
                  {project.objectives.map((obj) => (
                    <li key={obj.id} id={`objective-${obj.id}`} className="small">
                      ✅ <strong>{obj.title}</strong>: {obj.description}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
          </ul>
        </>
      )}
      
      {assistant.child_assistants && assistant.child_assistants.length > 0 && (
        <div className="mt-4 container ">
          <h5 className="d-flex align-items-center">
            🛠️ Tools / Sub-Assistants
            <button
              className="btn btn-sm btn-outline-secondary ms-2"
              onClick={() => setShowTools(!showTools)}
            >
              {showTools ? "Hide" : "Show"}
            </button>
          </h5>

          {showTools && (
            <ul className="list-group">
              {assistant.child_assistants.map((sub, index) => (
                <li key={index} className="list-group-item">
                  <Link to={`/assistants/${sub.slug}`}>
                    <strong>{sub.name}</strong>
                  </Link>
                  <p className="text-muted mb-0">{sub.description}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      
      <h4>🧠 Summary at a Glance</h4>
      <p><strong>Personality:</strong> {assistant.personality || "Not configured"}</p>
      <p><strong>Voice Style:</strong> {assistant.voice_style || "Default"}</p>
      <p><strong>Reasoning Style:</strong> {assistant.reasoning_style || "Analytical"}</p>
      <p><strong>Planning Mode:</strong> {assistant.planning_mode || "Goal-Driven"}</p>
      <p><strong>Memory Mode:</strong> {assistant.memory_mode || "Short-Term"}</p>
      <p><strong>Preferred Model:</strong> {assistant.preferred_model || "N/A"}</p>
      {assistant.is_primary && (
        <p>
          <strong>Primary Role:</strong> ✅ System Orchestrator
        </p>
      )}
    </div>
  );
}