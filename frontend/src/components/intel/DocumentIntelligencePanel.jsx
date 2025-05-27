import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { Spinner } from "react-bootstrap";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { suggestAssistant } from "../../api/assistants";
import { USE_PROMPT_MODE } from "../../config/ui";

export default function DocumentIntelligencePanel({ docId }) {
  const [summary, setSummary] = useState(null);
  const [config, setConfig] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingConfig, setLoadingConfig] = useState(false);
  const [bootstrapping, setBootstrapping] = useState(false);
  const navigate = useNavigate();

  const handleSummarize = async () => {
    setLoadingSummary(true);
    setSummary(null);
    try {
      const res = await apiFetch(`/intel/documents/${docId}/summarize_with_context/`, {
        method: "POST",
      });
      setSummary(res.summary);
    } catch (err) {
      setSummary("❌ Failed to generate summary");
      console.error(err);
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleBootstrapAgent = async () => {
    setBootstrapping(true);
    try {
      const res = await apiFetch(
        USE_PROMPT_MODE === "legacy"
          ? `/intel/intelligence/bootstrap-assistant/${docId}/`
          : "/assistants/from-document-set/",
        {
          method: "POST",
          body:
            USE_PROMPT_MODE === "legacy"
              ? undefined
              : {
                  document_set_id: docId,
                },
        }
      );

      const { slug, thread_id, project_id, memory_id, objective_id } = res;

      const queryParams = new URLSearchParams();
      if (thread_id) queryParams.append("thread", thread_id);
      if (project_id) queryParams.append("project", project_id);
      if (memory_id) queryParams.append("memory", memory_id);
      if (objective_id) queryParams.append("objective", objective_id);

      console.log("📎 Thread ID:", thread_id);
      console.log("🧠 Bootstrap success:", res);

      navigate(`/assistants/${slug}?${queryParams.toString()}`);
    } catch (err) {
      console.error("Bootstrap failed:", err);
      toast.error("Failed to create assistant from document.");
    } finally {
      setBootstrapping(false);
    }
  };

  const handleSuggest = async () => {
    try {
      const data = await suggestAssistant({
        context_summary: summary || "",
        tags: [],
        recent_messages: [],
      });
      if (data.suggested_assistant) {
        alert(
          `Suggested assistant: ${data.suggested_assistant.name}\nReason: ${data.reasoning}`
        );
      } else {
        alert("No suggestion available");
      }
    } catch (err) {
      alert("Failed to get suggestion");
    }
  };

  return (
    <div className="mt-4 border-top pt-3">
      <h5>🧠 AI Intelligence Tools</h5>

      <div className="d-flex gap-2 mb-3">
        <button className="btn btn-outline-info" onClick={handleSummarize} disabled={loadingSummary}>
          {loadingSummary ? <Spinner size="sm" /> : "🔍 Generate Summary"}
        </button>
        <div className="my-3 d-flex gap-3">
      <button
        className="btn btn-outline-success"
        onClick={handleBootstrapAgent}
        disabled={bootstrapping}
      >
        {bootstrapping ? (
          <>
            <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
            Bootstrapping...
          </>
        ) : (
          "🤖 Bootstrap Assistant"
        )}
      </button>
      <button className="btn btn-outline-primary" onClick={handleSuggest}>
        🤖 Suggest Assistant
      </button>
        </div>
      </div>

      {summary && (
        <div className="alert alert-info">
          <strong>Summary:</strong>
          <p className="mb-0">{summary}</p>
        </div>
      )}

      {config && (
        <div className="alert alert-success">
          <strong>Assistant Config:</strong>
          <pre className="mb-0 small">
            {typeof config === "string" ? config : JSON.stringify(config, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}