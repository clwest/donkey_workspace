import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import ProjectTaskManager from "./ProjectTaskManagerPage";
import AssistantPromptPanel from "../../../components/assistant/AssistantPromptPanel";
import AssistantIntelligencePanel from "../../../components/assistant/AssistantIntelligencePanel";
import useAutoReflectionLoop from "../../../components/assistant/AutoModeController";
import AutoModeToggle from "../../../components/assistant/AutoModeToggle";
import PrimaryStar from "../../../components/assistant/PrimaryStar";
import AssistantSpawnForm from "../../../components/assistant/AssistantSpawnForm";
import SwarmMemoryViewer from "../../../components/agents/SwarmMemoryViewer";
import SwarmTimelineViewer from "../../../components/agents/SwarmTimelineViewer";
import apiFetch from "../../../utils/apiClient";
import ProjectRolesRow from "../../../components/assistant/roles/ProjectRolesRow";
import ProjectHistoryPanel from "../../../components/assistant/project_history/ProjectHistoryPanel";
import ContinuityModal from "../../../components/assistant/ContinuityModal";

export default function ProjectDetailPage() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [linkedMemories, setLinkedMemories] = useState([]);
  const [availableMemories, setAvailableMemories] = useState([]);
  const [selectedMemoryId, setSelectedMemoryId] = useState("");
  const [saving, setSaving] = useState(false);
  const [aiPlan, setAiPlan] = useState("");
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [autoMode, setAutoMode] = useState(false);
  const { isRunning } = useAutoReflectionLoop(id, autoMode);
  const [assistants, setAssistants] = useState([]);
  const [selectedAssistantId, setSelectedAssistantId] = useState("");
  const [changeMode, setChangeMode] = useState(false);
  const [teamMemory, setTeamMemory] = useState([]);
  const [showContinuity, setShowContinuity] = useState(false);

  useEffect(() => {
    async function loadTeamMemory() {
      if (!project || !project.core_project_id) {
        return;
      }

      try {
        const data = await apiFetch(`/projects/${project.core_project_id}/team_memory/`);
        setTeamMemory(data);
      } catch (err) {
        console.error("Failed to load team memory", err);
      }
    }

    loadTeamMemory();
  }, [project]);

  // === Initial Project + Memories ===
  useEffect(() => {
    if (!id) {
      console.warn("ProjectDetailPage: missing project id");
      return;
    }
    async function loadInitialData() {
      try {
        const [projectData, memoryList, linkedList, assistantsList] = await Promise.all([
          apiFetch(`/assistants/projects/${id}/`),
          apiFetch(`/memory/list/`),
          apiFetch(`/assistants/projects/${id}/linked_memories/`),
          apiFetch(`/assistants/`),
        ]);
        setProject(projectData);
        setAvailableMemories(memoryList);
        setLinkedMemories(linkedList);
        setAssistants(assistantsList);
        setSelectedAssistantId(projectData.assistant?.id || "");
      } catch (err) {
        toast.error("⚠️ Error loading project or memories.");
        console.error("Initial load error:", err);
      }
    }

    loadInitialData();
  }, [id]);

  // === Thoughts ===
  useEffect(() => {
    if (!id) {
      console.warn("ProjectDetailPage: missing project id");
      return;
    }
    const loadThoughts = async () => {
      try {
        const thoughtsRes = await apiFetch(`/assistants/projects/${id}/thoughts/`);
        setThoughts(thoughtsRes);
        toast.success("🧠 Assistant thoughts loaded!");
      } catch (err) {
        toast.error("⚠️ Failed to load thoughts.");
        console.error("Failed to fetch thoughts:", err);
      } finally {
        setLoading(false);
      }
    };

    loadThoughts();
  }, [id]);

  // === Link Memory ===
  async function handleLinkMemory() {
    if (!selectedMemoryId) return;
    try {
      await apiFetch("/assistants/projects/link_memory/", {
        method: "POST",
        body: {
          project_id: id,
          memory_id: selectedMemoryId,
        },
      });
      toast.success("📌 Memory linked!");
      window.location.reload();
    } catch (err) {
      toast.error("❌ Failed to link memory.");
      console.error(err);
    }
  }

  // === Assign Assistant ===
  async function handleAssignAssistant() {
    try {
      await apiFetch(`/assistants/projects/${id}/`, {
        method: "PATCH",
        body: { assistant: selectedAssistantId },
      });
      toast.success("✅ Assistant assigned to project!");
      setProject(prev => ({
        ...prev,
        assistant: assistants.find(a => a.id === selectedAssistantId)
      }));
      setChangeMode(false);
    } catch (err) {
      toast.error("❌ Failed to assign assistant.");
      console.error(err);
    }
  }

  // === AI Plan ===
  async function handleAIPlan() {
    try {
      const data = await apiFetch(`/assistants/projects/${id}/ai_plan/`, { method: "POST" });
      if (data.result) {
        setAiPlan(data.result);
        toast.info("🤖 AI Plan generated!");
      } else {
        toast.warn("⚠️ No result returned from AI Plan.");
      }
    } catch (err) {
      toast.error("❌ Error generating AI plan.");
      console.error(err);
    }
  }

  async function handleAcceptAIPlan() {
    if (!aiPlan) return;

    const confirmSave = window.confirm(
      "This will overwrite current tasks with AI suggestions. Proceed?"
    );
    if (!confirmSave) return;

    setSaving(true);
    try {
      const parsedTasks = aiPlan
        .split("\n")
        .filter((line) => line.trim().startsWith("- "))
        .map((line) => line.replace(/^-\s*/, "").trim());

      await apiFetch(`/assistants/projects/${id}/tasks/clear/`, { method: "POST" });

      for (let task of parsedTasks) {
        await apiFetch(`/assistants/projects/${id}/tasks/create/`, {
          method: "POST",
          body: { content: task },
        });
      }

      toast.success("✅ AI Plan saved!");
      window.location.reload();
    } catch (err) {
      toast.error("❌ Failed to save AI plan.");
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  if (!project) return <div className="container my-5">Loading project...</div>;

  return (
    <>
    <div className="container my-5">
      <h1 className="mb-4">{project.title}</h1>
      {project.team && project.team.length > 0 && (
        <div className="mb-3">
          <h6 className="text-muted">Team</h6>
          <ul className="list-unstyled">
            {project.team.map((member) => (
              <li key={member.id}>
                {member.name} - {project.roles?.[member.id] || "member"}
              </li>
            ))}
          </ul>
        </div>
      )}
      {teamMemory.length > 0 && (
        <div className="mb-3">
          <h6 className="text-muted">Team Memory Chain</h6>
          <ul className="list-unstyled">
            {teamMemory.slice(0, 5).map((m) => (
              <li key={m.id}>{m.event.slice(0, 60)}</li>
            ))}
          </ul>
        </div>
      )}
      <ProjectRolesRow projectId={id} />

      {/* Assistant Selector */}
      <div className="mb-4">
        <label className="form-label">👤 Assigned Assistant</label>

        {project.assistant && !changeMode ? (
          <div className="d-flex justify-content-between align-items-center">
            <div className="fw-semibold">
              {project.assistant.name}
              <PrimaryStar isPrimary={project.assistant.is_primary} />
            </div>
            <button
              className="btn btn-sm btn-outline-secondary"
              onClick={() => setChangeMode(true)}
            >
              Change Assistant
            </button>
          </div>
        ) : (
          <div className="d-flex gap-2">
            <select
              id="assistant-select"
              className="form-select"
              value={selectedAssistantId}
              onChange={(e) => setSelectedAssistantId(e.target.value)}
            >
              <option value="">None</option>
              {assistants
                .filter((a) => a && a.id)
                .map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name || "Unnamed Assistant"}
                  </option>
              ))}
            </select>
            <button
              className="btn btn-outline-primary"
              onClick={handleAssignAssistant}
              disabled={!selectedAssistantId}
            >
              Assign
            </button>
          </div>
        )}
      </div>

      <AssistantSpawnForm creatorId={selectedAssistantId} projectId={project.id} />


      <AutoModeToggle enabled={autoMode} onToggle={setAutoMode} />
      <div className="my-3">
        <button
          className="btn btn-outline-secondary"
          onClick={() => setShowContinuity(true)}
          disabled={!project.assistant}
        >
          Continuity Check
        </button>
      </div>
      <AssistantPromptPanel projectId={project.id} />
      <AssistantIntelligencePanel projectId={id} />
      <ProjectTaskManager />
      <ProjectHistoryPanel projectId={id} />
      <SwarmMemoryViewer />
      <SwarmTimelineViewer />

    {project?.dev_docs?.length > 0 && (
      <ul className="list-group">
        {project.dev_docs.map((doc) => (
          <li key={doc.slug} className="list-group-item">
            <strong>{doc.title}</strong>
            <p className="mb-1 small text-muted">
              {doc.content ? doc.content.slice(0, 120) + "..." : <em>No preview</em>}
            </p>
            <button
              className="btn btn-sm btn-outline-primary mt-2"
              onClick={async () => {
                try {
                  const res = await apiFetch("/assistants/thoughts/reflect-on-doc/", {
                    method: "POST",
                    body: {
                      doc_id: doc.id,
                      assistant_id: selectedAssistantId,
                      project_id: project.id,
                    },
                  });
                  console.log(res);
                  toast.success("🧠 Zeno has reflected on this doc!");
                } catch (err) {
                  console.error(err);
                  toast.error("❌ Failed to reflect on doc.");
                }
              }}
            >
              Reflect on This
            </button>
          </li>
        ))}
      </ul>
    )}
    </div>
    <ContinuityModal
      show={showContinuity}
      onClose={() => setShowContinuity(false)}
      assistantSlug={project.assistant?.slug}
      projectId={project.id}
    />
    </>
  );
}