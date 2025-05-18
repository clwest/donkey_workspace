import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import LoadingSpinner from "../../components/LoadingSpinner";
import Modal from "../../components/CommonModal";
import PromptUsageLogTable from "../../components/prompts/PromptUsageLogTable";
import PromptUsageLogList from "../../components/prompts/PromptUsageLogList";
import PromptDiagnosticsPanel from "../../components/prompts/PromptDiagnosticPanel";

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
      const res = await fetch(`/api/prompts/${slug}/`);
      const data = await res.json();
      if (res.ok) {
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
      const res = await fetch("/api/assistants/");
      const data = await res.json();
      if (res.ok) setAssistants(data);
    } catch (err) {
      console.error("Error loading assistants:", err);
    }
  }

  async function handleAssign() {
    try {
      const res = await fetch(`/api/prompts/${slug}/assign/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assistant_id: selectedAssistantId }),
      });
      if (res.ok) {
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

        <button className="btn btn-danger" onClick={async () => {
          if (!window.confirm("Are you sure you want to delete this prompt?")) return;
          try {
            const res = await fetch(`/api/prompts/${slug}/`, { method: "DELETE" });
            if (res.ok) {
              toast.success("✅ Prompt deleted");
              navigate("/prompts");
            } else {
              toast.error("❌ Failed to delete");
            }
          } catch (err) {
            console.error("Delete failed", err);
          }
        }}>
          🗑️ Delete Prompt
        </button>
      </div>
    </div>
  );
}
