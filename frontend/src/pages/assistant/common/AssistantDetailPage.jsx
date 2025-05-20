import { useEffect, useState } from "react";
import { useParams, Link, useLocation } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import PrimaryStar from "../../../components/assistant/PrimaryStar";
import MoodStabilityGauge from "../../../components/assistant/MoodStabilityGauge";
import DriftScoreChart from "../../../components/assistant/DriftScoreChart";
import RecoveryPanel from "../../../components/assistant/RecoveryPanel";
import { runDriftCheck, runSelfAssessment } from "../../../api/assistants";
import SelfAssessmentModal from "../../../components/assistant/SelfAssessmentModal";
import { toast } from "react-toastify";
import "./styles/AssistantDetail.css";
import AssistantMemoryAuditPanel from "../../../components/assistant/memory/AssistantMemoryAuditPanel";

export default function AssistantDetailPage() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const [showTools, setShowTools] = useState(false);
  const [availableDocs, setAvailableDocs] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState("");
  const [reflectAfter, setReflectAfter] = useState(false);
  const [linking, setLinking] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [assessment, setAssessment] = useState(null);
  const [showAssess, setShowAssess] = useState(false);
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
    async function fetchDocs() {
      try {
        const res = await apiFetch(`/intel/documents/?exclude_for=${slug}&limit=50`);
        setAvailableDocs(res);
      } catch (err) {
        console.error("Failed to load documents", err);
      }
    }
    fetchDocs();
  }, [slug]);

  useEffect(() => {
    if (threadId) {
      console.log("📍 Would fetch thread:", threadId);
      // TODO: fetch thread data or display something visually
    }
    if (memoryId) {
      toast.success("Assistant created and linked to memory!");
      setTimeout(() => {
        document
          .getElementById(`memory-${memoryId}`)
          ?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    }
    if (objectiveId) {
      toast.info("Linked objective ready!");
      setTimeout(() => {
        document
          .getElementById(`objective-${objectiveId}`)
          ?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    }
  }, [threadId, memoryId, objectiveId]);

  const handleLinkDocument = async (e) => {
    e.preventDefault();
    if (!selectedDoc) return;
    setLinking(true);
    try {
      await apiFetch(`/assistants/${slug}/add_document/`, {
        method: "POST",
        body: { document_id: selectedDoc, reflect: reflectAfter },
      });
      const data = await apiFetch(`/assistants/${slug}/`);
      setAssistant(data);
      toast.success("Document linked");
      setSelectedDoc("");
    } catch (err) {
      console.error("Link failed", err);
      toast.error("Failed to link document");
    } finally {
      setLinking(false);
    }
  };

  const handleSelfAssess = async () => {
    try {
      const res = await runSelfAssessment(slug);
      setAssessment(res);
      setShowAssess(true);
    } catch (err) {
      toast.error("Self assessment failed");
    }
  };

  if (!assistant)
    return <div className="container my-5">Loading assistant...</div>;

  return (
    <div className="container my-5">
      <h1 className="display-4 d-flex align-items-center">
        {assistant.name}
        <PrimaryStar isPrimary={assistant.is_primary} />
        <MoodStabilityGauge msi={assistant.mood_stability_index} />
      </h1>
      <p className="text-muted">Assistant Details Page</p>
      <div className="mb-3">
        <ul className="nav nav-tabs">
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "overview" ? "active" : ""}`}
              onClick={() => setActiveTab("overview")}
            >
              Overview
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "memory" ? "active" : ""}`}
              onClick={() => setActiveTab("memory")}
            >
              🧠 Memory Audit
            </button>
          </li>
        </ul>
      </div>
      {activeTab === "overview" && (
        <>
      {assistant.recent_drift && (
        <div className="alert alert-warning">🧬 Drift Detected: {assistant.recent_drift.summary}</div>
      )}

      <div className="mb-4">
        <p>
          <strong>Slug:</strong> {assistant.slug}
        </p>
        <p>
          <strong>Description:</strong>{" "}
          {assistant.description || "No description yet."}
        </p>
        <p>
          <strong>Specialty:</strong> {assistant.specialty || "N/A"}
        </p>
        <p>
          <strong>Status:</strong> {assistant.is_active ? "Active" : "Inactive"}
        </p>
        <p>
          <strong>Created:</strong>{" "}
          {new Date(assistant.created_at).toLocaleString()}
        </p>
      </div>

      {assistant.current_project ? (
        <div className="alert alert-info">
          Assigned Project: {assistant.current_project.title} (
          {assistant.current_project.objective_count} objectives)
        </div>
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
        <Link to={`/assistants/${slug}/chat`} className="btn btn-dark">
          💬 Chat
        </Link>
        <Link
          to={`/assistants/${slug}/thoughts`}
          className="btn btn-outline-primary"
        >
          🧠 Thought Log
        </Link>
        <Link
          to={`/assistants/${slug}/projects`}
          className="btn btn-outline-success"
        >
          📂 Projects
        </Link>
        <Link
          to={`/assistants/${slug}/objectives`}
          className="btn btn-outline-success"
        >
          🗂️ Project Objectives
        </Link>
        <Link
          to={`/assistants/${slug}/memories`}
          className="btn btn-outline-warning"
        >
          📘 Memory
        </Link>
        <Link
          to={`/assistants/${slug}/reflect`}
          className="btn btn-outline-info"
        >
          🔍 Reflections
        </Link>
        <Link
          to={`/assistants/${slug}/sessions`}
          className="btn btn-outline-secondary"
        >
          💬 Sessions
        </Link>
        <Link
          to={`/assistants/${slug}/trace`}
          className="btn btn-outline-secondary"
        >
          🧬 Delegation Trace
        </Link>
        <Link
          to={`/assistants/${assistant.slug}/dashboard`}
          className="btn btn-outline-primary"
        >
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

      <div className="mb-4">
        <h6>🔗 Link Document</h6>
        <form onSubmit={handleLinkDocument} className="d-flex align-items-end gap-2">
          {availableDocs.length > 0 ? (
            <select
              className="form-select"
              value={selectedDoc}
              onChange={(e) => setSelectedDoc(e.target.value)}
            >
              <option value="">Select document</option>
              {availableDocs.map((d) => (
                <option key={d.id} value={d.id}>
                  {`${d.title} (${d.source_type}) - ${new Date(d.created_at).toLocaleDateString()}`}
                </option>
              ))}
            </select>
          ) : (
            <p className="mb-0 text-muted">No documents available</p>
          )}
          <div className="form-check ms-2">
            <input
              className="form-check-input"
              type="checkbox"
              id="reflectAfter"
              checked={reflectAfter}
              onChange={(e) => setReflectAfter(e.target.checked)}
            />
            <label className="form-check-label" htmlFor="reflectAfter">
              Reflect after linking
            </label>
          </div>
          <button className="btn btn-primary" type="submit" disabled={linking}>
            {linking ? "Linking..." : "Link"}
          </button>
        </form>
      </div>

      {assistant.projects?.length > 0 && (
        <>
          <h5 className="mt-4">📂 Linked Projects</h5>
          <ul className="list-group mb-3">
            {assistant.projects.map((project) => (
              <li
                key={project.id}
                id={`project-${project.id}`}
                className="list-group-item"
              >
                <Link to={`/assistants/projects/${project.id}`}>
                  {project.title}
                </Link>
                {project.objectives?.length > 0 && (
                  <ul className="mt-2 ms-3">
                    {project.objectives.map((obj) => (
                      <li
                        key={obj.id}
                        id={`objective-${obj.id}`}
                        className="small"
                      >
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

      {assistant.skills && assistant.skills.length > 0 && (
        <div className="mt-4">
          <h5 className="d-flex align-items-center">
            🧠 Skills
            <Link
              to={`/assistants/${slug}/skillgraph`}
              className="btn btn-sm btn-outline-secondary ms-2"
            >
              Graph
            </Link>
          </h5>
          <ul className="list-group">
            {assistant.skills.map((skill, idx) => (
              <li key={idx} className="list-group-item">
                <strong>{skill.name}</strong> - {skill.description || ""}
                <div className="progress mt-1" style={{ height: "4px" }}>
                  <div
                    className="progress-bar"
                    style={{ width: `${skill.confidence * 100}%` }}
                  ></div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {assistant.drift_logs && assistant.drift_logs.length > 0 && (
        <div className="mt-4">
          <h5>🧬 Drift Over Time</h5>
          <DriftScoreChart logs={assistant.drift_logs} />
        </div>
      )}

      <RecoveryPanel assistantSlug={slug} />

      <hr />
      <h4>🪪 Identity</h4>
      <p>
        <strong>Persona:</strong> {assistant.persona_summary || "None"}
      </p>
      <p>
        <strong>Motto:</strong> {assistant.motto || "N/A"}
      </p>
      {assistant.traits && (
        <p>
          <strong>Traits:</strong>
          {Object.entries(assistant.traits).map(([k, v]) => (
            <span key={k} className="badge bg-secondary ms-2">
              {k}:{v ? "✅" : "❌"}
            </span>
          ))}
        </p>
      )}
      {assistant.values && assistant.values.length > 0 && (
        <p>
          <strong>Values:</strong> {assistant.values.join(", ")}
        </p>
      )}
      <button
        className="btn btn-outline-info mb-3"
        onClick={async () => {
          await apiFetch(`/assistants/${slug}/self_reflect/`, {
            method: "POST",
          });
          const data = await apiFetch(`/assistants/${slug}/`);
          setAssistant(data);
        }}
      >
        Reflect on Self
      </button>
      <button
        className="btn btn-outline-warning mb-3 ms-2"
        onClick={async () => {
          try {
            await runDriftCheck(slug);
            const data = await apiFetch(`/assistants/${slug}/`);
            setAssistant(data);
            toast.info("Drift analysis complete");
          } catch (err) {
            toast.error("Drift check failed");
          }
        }}
      >
        Check Drift
      </button>
      <button
        className="btn btn-outline-info mb-3 ms-2"
        onClick={handleSelfAssess}
      >
        Run Self-Assessment
      </button>

      <h4>🧠 Summary at a Glance</h4>
      <p>
        <strong>Personality:</strong>{" "}
        {assistant.personality || "Not configured"}
      </p>
      <p>
        <strong>Voice Style:</strong> {assistant.voice_style || "Default"}
      </p>
      <p>
        <strong>Reasoning Style:</strong>{" "}
        {assistant.reasoning_style || "Analytical"}
      </p>
      <p>
        <strong>Planning Mode:</strong>{" "}
        {assistant.planning_mode || "Goal-Driven"}
      </p>
      <p>
        <strong>Memory Mode:</strong> {assistant.memory_mode || "Short-Term"}
      </p>
      <p>
        <strong>Preferred Model:</strong> {assistant.preferred_model || "N/A"}
      </p>
      {assistant.is_primary && (
        <p>
          <strong>Primary Role:</strong> ✅ System Orchestrator
        </p>
      )}
    </>
  )}
  {activeTab === "memory" && (
    <AssistantMemoryAuditPanel assistant={assistant} />
  )}
  <SelfAssessmentModal
    show={showAssess}
    onClose={() => setShowAssess(false)}
    result={assessment}
  />
  </div>
  );
}
