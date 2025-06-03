import { useEffect, useState } from "react";
import { useParams, Link, useLocation } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import PrimaryStar from "../../../components/assistant/PrimaryStar";
import MoodStabilityGauge from "../../../components/assistant/MoodStabilityGauge";
import DriftScoreChart from "../../../components/assistant/DriftScoreChart";
import RecoveryPanel from "../../../components/assistant/RecoveryPanel";
import {
  runDriftCheck,
  runSelfAssessment,
  assignPrimaryAssistant,
  setAssistantActive,
} from "../../../api/assistants";
import SelfAssessmentModal from "../../../components/assistant/SelfAssessmentModal";
import { toast } from "react-toastify";
import "./styles/AssistantDetail.css";
import AssistantMemoryAuditPanel from "../../../components/assistant/memory/AssistantMemoryAuditPanel";
import AssistantMemoryPanel from "../../../components/assistant/memory/AssistantMemoryPanel";
import AgentTrainingManager from "../../../components/assistants/AgentTrainingManager";
import ReflectNowButton from "../../../components/assistant/ReflectNowButton";

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
  const [reflecting, setReflecting] = useState(false);
  const [assessing, setAssessing] = useState(false);
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState("");
  const threadId = query.get("thread");
  const projectId = query.get("project");
  const memoryId = query.get("memory");
  const objectiveId = query.get("objective");

  // Clear state when navigating between assistants so new data loads properly
  useEffect(() => {
    setAssistant(null);
    setAvailableDocs([]);
    setSelectedDoc("");
    setActiveTab("overview");
    setAssessment(null);
    setShowAssess(false);
    setReflecting(false);
    setAssessing(false);
    setEditingName(false);
    setNameInput("");
  }, [slug]);

  useEffect(() => {
    async function fetchAssistant() {
      try {
        const data = await apiFetch(`/assistants/${slug}/`);
        setAssistant(data);
        setNameInput(data.name);
      } catch (err) {
        console.error("Error fetching assistant:", err);
      }
    }
    fetchAssistant();
  }, [slug]);

  useEffect(() => {
    async function fetchDocs() {
      try {
        const res = await apiFetch(
          `/intel/documents/?exclude_for=${slug}&limit=50`,
        );
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
    setAssessing(true);
    try {
      const res = await runSelfAssessment(slug);
      setAssessment(res);
      setShowAssess(true);
    } catch (err) {
      toast.error("Self assessment failed");
    } finally {
      setAssessing(false);
    }
  };

  const handleSelfReflect = async () => {
    setReflecting(true);
    try {
      await apiFetch(`/assistants/${slug}/self_reflect/`, {
        method: "POST",
      });
      const data = await apiFetch(`/assistants/${slug}/`);
      setAssistant(data);
      toast.success("Reflection complete");
    } catch (err) {
      toast.error("Self reflection failed");
    } finally {
      setReflecting(false);
    }
  };

  const handleEndUse = async () => {
    if (!assistant?.current_project) return;
    if (!window.confirm("Mark current project as completed?")) return;
    try {
      await apiFetch(`/assistants/projects/${assistant.current_project.id}/`, {
        method: "PATCH",
        body: { status: "completed" },
      });
      const data = await apiFetch(`/assistants/${slug}/`);
      setAssistant(data);
      toast.success("Project marked completed");
    } catch (err) {
      console.error("Failed to end use", err);
      toast.error("Failed to complete project");
    }
  };

  const handleToggleActive = async () => {
    const confirmMsg = assistant.is_active
      ? "Deactivate this assistant?"
      : "Reactivate this assistant?";
    if (!window.confirm(confirmMsg)) return;
    try {
      const data = await setAssistantActive(slug, !assistant.is_active);
      setAssistant(data);
      toast.success(
        assistant.is_active ? "Assistant deactivated" : "Assistant reactivated",
      );
    } catch (err) {
      toast.error("Failed to update status");
    }
  };

  if (!assistant)
    return <div className="container my-5">Loading assistant...</div>;

  return (
    <div className="container my-5">
      <h1 className="display-4 d-flex align-items-center">
        {editingName ? (
          <>
            <input
              type="text"
              className="form-control form-control-sm me-2"
              value={nameInput}
              onChange={(e) => setNameInput(e.target.value)}
              style={{ maxWidth: "300px" }}
            />
            <button
              className="btn btn-sm btn-primary me-2"
              onClick={async () => {
                try {
                  const data = await apiFetch(`/assistants/${slug}/`, {
                    method: "PATCH",
                    body: { name: nameInput },
                  });
                  setAssistant(data);
                  setEditingName(false);
                  toast.success("Name updated");
                } catch (err) {
                  toast.error("Failed to update name");
                }
              }}
            >
              Save
            </button>
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => {
                setEditingName(false);
                setNameInput(assistant.name);
              }}
            >
              Cancel
            </button>
          </>
        ) : (
          <>
            {assistant.name}
            <button
              className="btn btn-link btn-sm ms-2"
              onClick={() => setEditingName(true)}
              title="Edit name"
            >
              ✏️
            </button>
          </>
        )}
        <PrimaryStar isPrimary={assistant.is_primary} />
        <MoodStabilityGauge score={assistant.health_score} />
        {!assistant.is_primary && (
          <button
            className="btn btn-sm btn-outline-warning ms-3"
            onClick={async () => {
              try {
                await assignPrimaryAssistant(slug);
                const data = await apiFetch(`/assistants/${slug}/`);
                setAssistant(data);
                toast.success("Assigned as Primary");
              } catch (err) {
                toast.error("Failed to assign primary");
              }
            }}
          >
            ⭐ Assign as Primary
          </button>
        )}
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
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "training" ? "active" : ""}`}
              onClick={() => setActiveTab("training")}
            >
              Agent Training
            </button>
          </li>
        </ul>
      </div>
      {activeTab === "overview" && (
        <>
          {assistant.recent_drift && (
            <div className="alert alert-warning">
              🧬 Drift Detected: {assistant.recent_drift.summary}
            </div>
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
              <strong>Status:</strong>{" "}
              {assistant.is_active ? "Active" : "Inactive"}
              <button
                className={`btn btn-sm ms-2 ${assistant.is_active ? "btn-outline-danger" : "btn-outline-success"}`}
                onClick={handleToggleActive}
              >
                {assistant.is_active ? "Deactivate" : "Reactivate"}
              </button>
            </p>
            <p>
              <strong>Created:</strong>{" "}
              {new Date(assistant.created_at).toLocaleString()}
            </p>
          </div>

          {assistant.current_project ? (
            <div className="alert alert-info d-flex justify-content-between align-items-center">
              <span>
                Assigned Project: {assistant.current_project.title} (
                {assistant.current_project.objective_count} objectives)
              </span>
              <button
                className="btn btn-sm btn-outline-danger"
                onClick={handleEndUse}
              >
                End Use
              </button>
            </div>
          ) : (
            <button
              className="btn btn-outline-secondary mb-3"
              onClick={async () => {
                try {
                  const projects = await apiFetch(
                    `/assistants/${slug}/projects/`,
                  );
                  const id = prompt(
                    "Assign project by ID",
                    projects[0]?.id || "",
                  );
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
              to={`/assistants/projects`}
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
            {assistant.capabilities?.reflection && (
              <Link
                to={`/assistants/${slug}/reflect`}
                className="btn btn-outline-info"
              >
                🔍 Reflections
              </Link>
            )}
            <Link
              to={`/assistants/${slug}/sessions`}
              className="btn btn-outline-secondary"
            >
              💬 Sessions
            </Link>
            {assistant.capabilities?.delegation !== false && (
              <Link
                to={`/assistants/${slug}/trace`}
                className="btn btn-outline-secondary"
              >
                🧬 Delegation Trace
              </Link>
            )}
            {assistant.capabilities?.dashboard && (
              <Link
                to={`/assistants/${slug}/dashboard`}
                className="btn btn-outline-primary"
              >
                🧠 View Dashboard
              </Link>
            )}
            <Link
              to={`/assistants/${slug}/capabilities`}
              className="btn btn-outline-secondary"
            >
              ⚙️ Edit Capabilities
            </Link>
          </div>

          <hr />
          {assistant.documents?.length > 0 && (
            <>
              <h5 className="mt-4">📄 Linked Documents</h5>
              <ul className="list-group mb-3">
                {assistant.documents.map((doc) => (
                  <li
                    key={doc.id}
                    className="list-group-item d-flex justify-content-between align-items-center"
                  >
                    <Link to={`/intel/documents/${doc.id}`}>{doc.title}</Link>
                    <ReflectNowButton slug={slug} docId={doc.id} />
                  </li>
                ))}
              </ul>
            </>
          )}

          <div className="mb-4">
            <h6>🔗 Link Document</h6>
            <form
              onSubmit={handleLinkDocument}
              className="d-flex align-items-end gap-2"
            >
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
              <button
                className="btn btn-primary"
                type="submit"
                disabled={linking}
              >
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

          {assistant.child_assistants &&
            assistant.child_assistants.length > 0 && (
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

          <AssistantMemoryPanel slug={slug} />

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
              {Array.isArray(assistant.traits)
                ? assistant.traits.map((t, idx) => (
                    <span key={idx} className="badge bg-secondary ms-2">
                      {t}
                    </span>
                  ))
                : Object.entries(assistant.traits).map(([k, v]) => (
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
          {assistant.capabilities?.reflection && (
            <button
              className="btn btn-outline-info mb-3"
              onClick={handleSelfReflect}
              disabled={reflecting}
            >
              {reflecting ? (
                <>
                  <span
                    className="spinner-border spinner-border-sm me-2"
                    role="status"
                  />
                  Reflecting...
                </>
              ) : (
                "Reflect on Self"
              )}
            </button>
          )}
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
          {assistant.capabilities?.reflection && (
            <button
              className="btn btn-outline-info mb-3 ms-2"
              onClick={handleSelfAssess}
              disabled={assessing}
            >
              {assessing ? (
                <>
                  <span
                    className="spinner-border spinner-border-sm me-2"
                    role="status"
                  />
                  Running...
                </>
              ) : (
                "Run Self-Assessment"
              )}
            </button>
          )}

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
            <strong>Memory Mode:</strong>{" "}
            {assistant.memory_mode || "Short-Term"}
          </p>
          <p>
            <strong>Preferred Model:</strong>{" "}
            {assistant.preferred_model || "N/A"}
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
      {activeTab === "training" && (
        <AgentTrainingManager assistantSlug={slug} />
      )}
      <SelfAssessmentModal
        show={showAssess}
        onClose={() => setShowAssess(false)}
        result={assessment}
      />
    </div>
  );
}
