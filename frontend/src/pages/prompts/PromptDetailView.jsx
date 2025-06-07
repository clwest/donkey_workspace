import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import LoadingSpinner from "../../components/LoadingSpinner";
import Modal from "../../components/CommonModal";
import PromptUsageLogTable from "../../components/prompts/PromptUsageLogTable";
import PromptUsageLogList from "../../components/prompts/PromptUsageLogList";
import PromptDiagnosticsPanel from "../../components/prompts/PromptDiagnosticPanel";
import PrimaryStar from "../../components/assistant/PrimaryStar";
import PromptDangerZone from "../../components/prompts/PromptDangerZone";
import apiFetch from "@/utils/apiClient";

export default function PromptDetailView() {
  const { slug } = useParams();
  const navigate = useNavigate();

  const [prompt, setPrompt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mutationMode, setMutationMode] = useState("clarify");
  const [assistants, setAssistants] = useState([]);
  const [selectedAssistantId, setSelectedAssistantId] = useState("");


  useEffect(() => {
    fetchPrompt();
    fetchAssistants();
  }, [slug]);

  async function fetchPrompt() {
    try {
      const data = await apiFetch(`/prompts/${slug}/`);
      if (data) {
        setPrompt(data);
        setSelectedAssistantId(data.assistant?.id || "");
      } else {
        toast.error("❌ Failed to load prompt.");
      }
    } catch (err) {
      console.error("Error fetching prompt:", err);
    } finally {
      setLoading(false);
    }
  }

  async function fetchAssistants() {
    try {
      const data = await apiFetch("/assistants/");
      setAssistants(data);
    } catch (err) {
      console.error("Error loading assistants:", err);
    }
  }

  async function handleAssign() {
    try {
      const res = await apiFetch(`/prompts/${slug}/assign/`, {
        method: "POST",
        body: { assistant_id: selectedAssistantId },
      });
      if (res) {
        toast.success("✅ Prompt assigned to assistant!");
        fetchPrompt();
      } else {
        toast.error("❌ Failed to assign prompt.");
      }
    } catch (err) {
      console.error("Failed to assign:", err);
      toast.error("❌ Server error.");
    }
  }

  if (loading) return <LoadingSpinner />;

  if (!prompt) {
    return (
      <div className="container my-5 text-center">
        <h3>❌ Prompt not found.</h3>
        <button className="btn btn-outline-secondary mt-3" onClick={() => navigate("/prompts")}>🔙 Back to Prompts</button>
      </div>
    );
  }

  return (
    <div className="container my-5">
      <h1 className="mb-2">{prompt.title}</h1>

      <p className="text-muted mb-2">
        Assigned to: {prompt.assistant?.name || "None"}
        <PrimaryStar isPrimary={prompt.assistant?.is_primary} />
      </p>
      <p className="text-muted mb-4">
        Type: {prompt.type} | Source: {prompt.source} | Tokens: {prompt.token_count}
      </p>

      <div className="bg-light p-3 rounded mb-4">
        <pre className="mb-0 text-dark" style={{ whiteSpace: "pre-wrap" }}>{prompt.content}</pre>
      </div>

      <div className="row mb-4">
        <div className="col-md-6">
          <label className="form-label">Assign to Assistant</label>
          <div className="input-group">
            <select
              className="form-select"
              value={selectedAssistantId}
              onChange={(e) => setSelectedAssistantId(e.target.value)}
            >
              <option value="">-- Select Assistant --</option>
              {assistants.map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
            <button className="btn btn-outline-success" onClick={handleAssign} disabled={!selectedAssistantId}>
              ✅ Assign
            </button>
          </div>
        </div>
      </div>
        <PromptDiagnosticsPanel text={prompt.content} />
      <div className="row mb-4">
        <div className="col-md-6">
          <PromptUsageLogList promptSlug={prompt.slug} />
        </div>
        <div className="col-md-6">
          {/* <PromptUsageLogList  /> */}
        </div>
      </div>
      <div className="d-flex gap-3 align-items-center">

        <button className="btn btn-primary" onClick={() => navigate(`/prompts/${slug}/remix?mode=${mutationMode}`)}>
          ✨ Apply Mutation
        </button>
      </div>

      <PromptDangerZone slug={slug} />
    </div>
  );
}
