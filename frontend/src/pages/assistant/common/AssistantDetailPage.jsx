import { useEffect, useState } from "react";
import { useParams, Link, useLocation, useNavigate } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import PrimaryStar from "../../../components/assistant/PrimaryStar";
import MoodStabilityGauge from "../../../components/assistant/MoodStabilityGauge";
import DriftScoreChart from "../../../components/assistant/DriftScoreChart";
import RecoveryPanel from "../../../components/assistant/RecoveryPanel";
import AssistantDiagnosticsPanel from "../../../components/assistant/AssistantDiagnosticsPanel";
import AssistantBadgeIcon from "../../../components/assistant/AssistantBadgeIcon";
import AssistantSetupSummary from "../../../components/assistant/AssistantSetupSummary";
import useAuthGuard from "../../../hooks/useAuthGuard";
import {
  runDriftCheck,
  runSelfAssessment,
  assignPrimaryAssistant,
  setAssistantActive,
} from "../../../api/assistants";
import SelfAssessmentModal from "../../../components/assistant/SelfAssessmentModal";
import { toast } from "react-toastify";
import { Button } from "react-bootstrap";
import "./styles/AssistantDetail.css";
import AssistantMemoryAuditPanel from "../../../components/assistant/memory/AssistantMemoryAuditPanel";
import AssistantMemoryPanel from "../../../components/assistant/memory/AssistantMemoryPanel";
import DelegationSummaryPanel from "../../../components/assistant/memory/DelegationSummaryPanel";
import AgentTrainingManager from "../../../components/assistants/AgentTrainingManager";
import ReflectNowButton from "../../../components/assistant/ReflectNowButton";
import CommonModal from "../../../components/CommonModal";
import AssistantBootPanel from "../../../components/assistants/AssistantBootPanel";
import RagDebugPanel from "../../../components/assistant/RagDebugPanel";
import RagPlaybackPanel from "../../../components/assistant/RagPlaybackPanel";
import BadgePreviewPanel from "../../../components/assistant/BadgePreviewPanel";
import DriftSuggestionsPanel from "../../../components/assistant/DriftSuggestionsPanel";
import AssistantGlossaryConvergencePanel from "../../../components/assistant/memory/AssistantGlossaryConvergencePanel";
import VocabularyProgressPanel from "../../../components/assistant/memory/VocabularyProgressPanel";
import { fetchGlossaryMutations } from "../../../api/agents";
import HintBubble from "../../../components/HintBubble";
import useAssistantHints from "../../../hooks/useAssistantHints";
import TourProgressBar from "../../../components/onboarding/TourProgressBar";
import ReflectionPrimerPanel from "../../../components/assistant/ReflectionPrimerPanel";
import useUserInfo from "../../../hooks/useUserInfo";
import useGlossaryOverlay from "../../../hooks/glossary";
import GlossaryOverlayTooltip from "../../../components/GlossaryOverlayTooltip";

export default function AssistantDetailPage() {
  useAuthGuard();
  const { slug } = useParams();
  const navigate = useNavigate();
  const [assistant, setAssistant] = useState(null);
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const [showTools, setShowTools] = useState(false);
  const [availableDocs, setAvailableDocs] = useState([]);
  const [docLoading, setDocLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState("");
  const [reflectAfter, setReflectAfter] = useState(false);
  const [linking, setLinking] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [memoryStats, setMemoryStats] = useState(null);
  const [latestMemoryId, setLatestMemoryId] = useState(null);
  const [primerReflection, setPrimerReflection] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [showAssess, setShowAssess] = useState(false);
  const [reflecting, setReflecting] = useState(false);
  const [assessing, setAssessing] = useState(false);
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);
  const [showBoot, setShowBoot] = useState(false);
  const [lastSelfTest, setLastSelfTest] = useState(null);
  const [mutationCount, setMutationCount] = useState(0);
  const [firstQuestionSummary, setFirstQuestionSummary] = useState(null);
  const [showPrimer, setShowPrimer] = useState(false);
  const { hints, dismissHint } = useAssistantHints(slug);
  const userInfo = useUserInfo();
  const glossaryOverlays = useGlossaryOverlay('assistant_detail');
  const threadId = query.get("thread");
  const projectId = query.get("project");
  const memoryId = query.get("memory");
  const objectiveId = query.get("objective");
  const handleDiagnosticsRefresh = () => {
    setRefreshKey((k) => k + 1);
    reloadAssistant();
  };

  const handleDismissPrimer = () => {
    localStorage.setItem(`seen_reflection_primer_${slug}`, "1");
    setShowPrimer(false);
  };

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

  const reloadAssistant = async () => {
    try {
      const data = await apiFetch(`/assistants/${slug}/`);
      if (data.show_intro_splash) {
        navigate(`/assistants/${slug}/intro`, { replace: true });
        return;
      }
      setAssistant(data);
      setNameInput(data.name);
    } catch (err) {
      console.error("Error fetching assistant:", err);
    }
  };

  useEffect(() => {
    reloadAssistant();
  }, [slug]);

  useEffect(() => {
    async function loadMemoryStats() {
      try {
        const [memRes, reflRes] = await Promise.all([
          apiFetch(`/assistants/${slug}/memories/`),
          apiFetch(`/assistants/${slug}/reflections/`),
        ]);
        const memList = memRes.results || memRes;
        const reflList = reflRes.results || reflRes;
        setMemoryStats({
          memories: memList.length,
          reflections: reflList.length,
        });
        const primer = reflList.find((r) => r.is_primer);
        setPrimerReflection(primer || null);
        setLatestMemoryId(memList[0]?.id || null);
        if (
          reflList.length > 0 &&
          userInfo?.onboarding_complete &&
          !localStorage.getItem(`seen_reflection_primer_${slug}`)
        ) {
          setShowPrimer(true);
        }
      } catch (err) {
        console.error("Failed to load memory stats", err);
      }
    }
    if (slug) {
      loadMemoryStats();
    }
  }, [slug, refreshKey]);

  useEffect(() => {
    async function loadFirstQuestions() {
      try {
        const data = await apiFetch(`/assistants/${slug}/first_question_stats/`);
        setFirstQuestionSummary(data);
      } catch (err) {
        console.error("Failed to load question stats", err);
      }
    }
    if (slug) {
      loadFirstQuestions();
    }
  }, [slug]);

  useEffect(() => {
    if (
      userInfo?.onboarding_complete &&
      memoryStats?.reflections > 0 &&
      !localStorage.getItem(`seen_reflection_primer_${slug}`)
    ) {
      setShowPrimer(true);
    }
  }, [userInfo, memoryStats, slug]);

  useEffect(() => {
    async function loadMutationCount() {
      try {
        const res = await fetchGlossaryMutations({ assistant: slug });
        const items = res.results || res;
        const pending = items.filter((m) => m.status === "pending").length;
        setMutationCount(pending);
      } catch (err) {
        console.error("Failed to load mutations", err);
        setMutationCount(0);
      }
    }
    if (slug) {
      loadMutationCount();
    }
  }, [slug]);

  useEffect(() => {
    async function fetchDocs() {
      setDocLoading(true);
      try {
        const res = await apiFetch(
          `/intel/documents/?exclude_for=${slug}&limit=50`,
        );
        setAvailableDocs(res);
      } catch (err) {
        console.error("Failed to load documents", err);
      } finally {
        setDocLoading(false);
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
        <AssistantBadgeIcon
          badges={assistant.skill_badges}
          primaryBadge={assistant.primary_badge}
        />
        <MoodStabilityGauge score={assistant.health_score} />
        {lastSelfTest && (
          <span
            className={`badge ms-2 ${lastSelfTest.passed ? "bg-success" : "bg-danger"}`}
            title={new Date(lastSelfTest.timestamp).toLocaleString()}
          >
            {lastSelfTest.passed ? "✅" : "❌"}
          </span>
        )}
        <button
          className="btn btn-sm btn-outline-secondary ms-3"
          onClick={() => setShowBoot(true)}
        >
          Open Boot Diagnostics
        </button>
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
      <div className="mb-2">
        {glossaryOverlays.map((o) => (
          <GlossaryOverlayTooltip key={o.slug} {...o} />
        ))}
      </div>
      <TourProgressBar assistantSlug={slug} />
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
              className={`nav-link ${activeTab === "memtools" ? "active" : ""}`}
              onClick={() => setActiveTab("memtools")}
            >
              Memory Tools
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
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "ragdebug" ? "active" : ""}`}
              onClick={() => setActiveTab("ragdebug")}
            >
              RAG Debug
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "vocab" ? "active" : ""}`}
              onClick={() => setActiveTab("vocab")}
            >
              Vocabulary Progress
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "self" ? "active" : ""}`}
              onClick={() => setActiveTab("self")}
            >
              Self-Learning
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "setup" ? "active" : ""}`}
              onClick={() => setActiveTab("setup")}
            >
              Setup Summary
            </button>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to={`/assistants/${slug}/rag-drift`}>
              Glossary Drift
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to={`/assistants/${slug}/anchor-health`}>
              Anchor Health
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to={`/assistants/${slug}/glossary`}>
              📘 Glossary
              {mutationCount > 0 && (
                <span className="badge bg-warning text-dark ms-1">
                  💬 {mutationCount}
                </span>
              )}
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to={`/assistants/${slug}/diagnostics`}>
              Diagnostics
            </Link>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "badges" ? "active" : ""}`}
              onClick={() => setActiveTab("badges")}
            >
              Badges
            </button>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to={`/assistants/${slug}/badges`}>
              Badge Settings
            </Link>
          </li>
        </ul>
        <div className="mt-2">
          <Link to={`/anchor/mutations?assistant=${assistant.slug}`}>
            <Button variant="outline" className="mt-2">
              Review Glossary Suggestions
            </Button>
          </Link>
          <Link to={`/keeper/logs?assistant=${assistant.slug}`}>
            <Button variant="outline" className="mt-2 ms-2">Keeper Logs</Button>
          </Link>
        </div>
      </div>
      {activeTab === "overview" && (
        <>
          {showPrimer && (
            <ReflectionPrimerPanel
              slug={slug}
              onDismiss={handleDismissPrimer}
            />
          )}
          <AssistantDiagnosticsPanel
            slug={slug}
            onRefresh={handleDiagnosticsRefresh}
          />
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
            {assistant.skill_badges && assistant.skill_badges.length > 0 && (
              <p>
                <strong>Badges:</strong>{" "}
                {assistant.skill_badges.map((b) => (
                  <span key={b} className="badge bg-success me-1">
                    {b}
                  </span>
                ))}
              </p>
            )}
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
                to={`/assistants/${slug}/delegation-trace`}
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

          <div className="card p-3 mb-3">
            <h6 className="mb-2">RAG Debug Tools</h6>
            <div className="d-flex flex-wrap gap-2">
              <Link
                to={`/assistants/${slug}/rag-inspector`}
                className="btn btn-sm btn-outline-primary"
              >
                ⚖️ RAG Grounding Inspector
              </Link>
              <Link
                to={`/assistants/${slug}/rag-drift`}
                className="btn btn-sm btn-outline-secondary"
              >
                🔎 Glossary Drift Report
              </Link>
              <Link
                to={`/assistants/${slug}/reflections/drift_map`}
                className="btn btn-sm btn-outline-secondary"
              >
                🌡️ Drift Heatmap
              </Link>
              <Link
                to={`/assistants/${slug}/anchor-health`}
                className="btn btn-sm btn-outline-secondary"
              >
                📉 View Anchor Health
              </Link>
              <Link
                to={`/assistants/${slug}/diagnostics`}
                className="btn btn-sm btn-outline-danger"
              >
                ⚡️ RAG Diagnostics Runner
              </Link>
              <Link
                to={`/assistants/${slug}/replays/`}
                className="btn btn-sm btn-outline-info"
              >
                🔹 RAG Playback Logs
              </Link>
            </div>
          </div>

          <hr />
          {assistant.documents?.length > 0 && (
            <details className="mt-4">
              <summary className="h5">📄 Linked Documents</summary>
              <ul className="list-group mb-3 mt-2">
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
            </details>
          )}

          <div className="mb-4">
            <h6>🔗 Link Document</h6>
            <form
              onSubmit={handleLinkDocument}
              className="d-flex align-items-end gap-2"
            >
              {docLoading ? (
                <div className="placeholder-glow flex-grow-1">
                  <div
                    className="placeholder col-12"
                    style={{ height: 32 }}
                  ></div>
                </div>
              ) : availableDocs.length > 0 ? (
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
              <table className="table table-sm mb-3">
                <tbody>
                  {assistant.projects.map((project) => {
                    const stale =
                      !(project.objectives && project.objectives.length) &&
                      !(project.next_actions && project.next_actions.length);
                    return (
                      <tr
                        key={project.id}
                        id={`project-${project.id}`}
                        className={stale ? "opacity-50" : ""}
                      >
                        <td>
                          <Link to={`/assistants/projects/${project.id}`}>
                            {project.title}
                          </Link>
                          {project.objectives?.length > 0 && (
                            <ul className="mt-1 mb-0 small">
                              {project.objectives.map((obj) => (
                                <li key={obj.id} id={`objective-${obj.id}`}>
                                  {obj.title}
                                </li>
                              ))}
                            </ul>
                          )}
                        </td>
                        <td className="text-end">
                          {stale && (
                            <button
                              className="btn btn-sm btn-outline-danger"
                              onClick={async () => {
                                if (!window.confirm("Delete stale project?"))
                                  return;
                                try {
                                  await apiFetch(
                                    `/assistants/projects/${project.id}/`,
                                    { method: "DELETE" },
                                  );
                                  reloadAssistant();
                                  toast.success("Project removed");
                                } catch {
                                  toast.error("Delete failed");
                                }
                              }}
                            >
                              🗑️
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
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

          <AssistantMemoryPanel slug={slug} refreshKey={refreshKey} />
          {memoryStats && (
            <div className="alert alert-info mt-2">
              <strong>Memory Entries:</strong> {memoryStats.memories} |{" "}
              <strong>Recent Reflections:</strong> {memoryStats.reflections}
              {primerReflection && (
                <Link
                  to={`/assistants/${slug}/reflections/`}
                  className="ms-2 badge bg-warning text-dark"
                >
                  🧠 first reflection
                </Link>
              )}
            </div>
          )}
          {firstQuestionSummary && (
            <div className="alert alert-secondary mt-2">
              <h6>First Question Summary</h6>
              <ul className="mb-1">
                {firstQuestionSummary.top_questions.map((q, i) => (
                  <li key={i}>{q.text} ({q.count})</li>
                ))}
              </ul>
              <div className="small text-muted">
                Avg drift: {firstQuestionSummary.avg_drift}
              </div>
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
        <>
          <div className="text-end mb-2">
            <Link
              to={`/assistants/${slug}/rag-inspector`}
              className="btn btn-sm btn-outline-primary"
            >
              RAG Grounding Inspector
            </Link>
          </div>
          <DelegationSummaryPanel slug={slug} />
          <AssistantMemoryAuditPanel assistant={assistant} />
        </>
      )}
      {activeTab === "memtools" && (
        <>
          {memoryStats && (
            <div className="alert alert-info">
              <strong>Memories:</strong> {memoryStats.memories} |{" "}
              <strong>Reflections:</strong> {memoryStats.reflections}
              {primerReflection && (
                <Link
                  to={`/assistants/${slug}/reflections/`}
                  className="ms-2 badge bg-warning text-dark"
                >
                  🧠 first reflection
                </Link>
              )}
            </div>
          )}
          <div className="d-flex flex-wrap gap-2 mb-3">
            <Link
              to={`/assistants/${slug}/memory`}
              className="btn btn-outline-primary"
            >
              Assistant Memory
            </Link>
            <Link
              to={`/assistants/${slug}/timeline`}
              className="btn btn-outline-secondary"
            >
              Memory Timeline
            </Link>
            <Link
              to="/assistants/memory-chains"
              className="btn btn-outline-secondary"
            >
              Memory Chains
            </Link>
            {latestMemoryId && (
              <Link
                to={`/assistants/memory/${latestMemoryId}/to-task`}
                className="btn btn-outline-success"
              >
                Memory → Task
              </Link>
            )}
            <Link to="/memories/reflect" className="btn btn-outline-info">
              Reflect Memories
            </Link>
            <Link
              to={`/memory/sandbox/${assistant.id}`}
              className="btn btn-outline-warning"
            >
              Sandbox
            </Link>
          </div>
        </>
      )}
      {activeTab === "training" && (
        <AgentTrainingManager assistantSlug={slug} />
      )}
      {activeTab === "ragdebug" && (
        <>
          <RagPlaybackPanel slug={slug} />
          <RagDebugPanel slug={slug} />
          <AssistantGlossaryConvergencePanel />
          {hints.find((h) => h.id === "rag_intro" && !h.dismissed) && (
            <HintBubble
              content={hints.find((h) => h.id === "rag_intro").content}
              position={{ top: 80, right: 20 }}
              onDismiss={() => dismissHint("rag_intro")}
            />
          )}
        </>
      )}
      {activeTab === "vocab" && (
        <VocabularyProgressPanel assistantSlug={assistant.slug} />
      )}
      {activeTab === "self" && <DriftSuggestionsPanel slug={slug} />}
      {activeTab === "setup" && <AssistantSetupSummary assistantId={slug} />}
      {activeTab === "badges" && <BadgePreviewPanel slug={slug} />}
      <CommonModal
        show={showBoot}
        onClose={() => setShowBoot(false)}
        title="Boot Diagnostics"
      >
        <AssistantBootPanel
          assistant={assistant}
          onTestComplete={(res) => setLastSelfTest(res)}
        />
      </CommonModal>
      <SelfAssessmentModal
        show={showAssess}
        onClose={() => setShowAssess(false)}
        result={assessment}
      />
    </div>
  );
}
