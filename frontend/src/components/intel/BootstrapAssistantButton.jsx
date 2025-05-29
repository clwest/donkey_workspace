import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { Spinner } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";
import { createAssistantFromDocuments } from "../../api/assistants";
import { USE_PROMPT_MODE } from "../../config/ui";

export default function BootstrapAssistantButton({ docId }) {
  const [bootstrapping, setBootstrapping] = useState(false);
  const navigate = useNavigate();

  const handleBootstrap = async () => {
    setBootstrapping(true);
    try {
      const res =
        USE_PROMPT_MODE === "legacy"
          ? await apiFetch(`/intel/intelligence/bootstrap-assistant/${docId}/`, {
              method: "POST",
            })
          : await createAssistantFromDocuments(
              { document_ids: [docId] },
              { userInitiated: true }
            );

      const { slug, thread_id, project_id, memory_id, objective_id } = res;

      toast.success("🚀 Assistant bootstrapped successfully!");
      navigate(
        `/assistants/${slug}?thread=${thread_id}&project=${project_id}&memory=${memory_id}&objective=${objective_id}`
      );
    } catch (err) {
      console.error("Bootstrap failed:", err);
      toast.error("❌ Failed to create assistant from document.");
    } finally {
      setBootstrapping(false);
    }
  };

  return (
    <button
      className="btn btn-outline-success"
      onClick={handleBootstrap}
      disabled={bootstrapping}
    >
      {bootstrapping ? (
        <>
          <Spinner
            as="span"
            animation="border"
            size="sm"
            role="status"
            aria-hidden="true"
            className="me-2"
          />
          Bootstrapping...
        </>
      ) : (
        "🤖 Bootstrap Assistant"
      )}
    </button>
  );
}