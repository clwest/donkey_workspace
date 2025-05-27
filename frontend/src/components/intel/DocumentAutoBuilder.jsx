import { useState, useRef, useEffect } from "react";
import apiFetch from "../../utils/apiClient";
import { USE_PROMPT_MODE } from "../../config/ui";
import { Spinner } from "react-bootstrap";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

export default function DocumentAutoBuilder({ docId }) {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const logRef = useRef(null);
  const navigate = useNavigate();

  const addLog = (message, type = "info") => {
    setLogs((prev) => [...prev, { message, type, timestamp: new Date() }]);
  };

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  const handleCreateEverything = async () => {
    setIsLoading(true);
    setLogs([]);
    addLog("🚀 Starting full assistant bootstrap...");

    try {
      addLog("📨 Sending assistant creation request...");
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
      addLog("✅ Assistant created successfully", "success");

      if (thread_id) addLog(`🧵 Thread created: ${thread_id}`, "info");
      if (project_id) addLog(`📂 Project created: ${project_id}`, "info");
      if (memory_id) addLog(`🧠 Memory linked: ${memory_id}`, "info");
      if (objective_id) addLog(`🎯 Objective set: ${objective_id}`, "info");

      addLog("🎉 All components created! Redirecting...", "success");

      const queryParams = new URLSearchParams();
      if (thread_id) queryParams.append("thread", thread_id);
      if (project_id) queryParams.append("project", project_id);
      if (memory_id) queryParams.append("memory", memory_id);
      if (objective_id) queryParams.append("objective", objective_id);

      navigate(`/assistants/${slug}?${queryParams.toString()}`);
    } catch (err) {
      console.error(err);
      addLog("❌ Failed to bootstrap assistant", "danger");
      toast.error("Assistant creation failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-4 border-top pt-3">
      <h5>🛠️ Automated Assistant Builder</h5>

      <button
        className="btn btn-lg btn-outline-success mb-3"
        onClick={handleCreateEverything}
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
              className="me-2"
            />
            Creating Assistant...
          </>
        ) : (
          "⚙️ Create Everything"
        )}
      </button>

      <div
        ref={logRef}
        className="bg-dark text-light p-3 rounded border"
        style={{ maxHeight: "300px", overflowY: "auto", fontSize: "0.85rem" }}
      >
        {logs.map((log, idx) => (
          <div key={idx} className={`text-${log.type === "danger" ? "danger" : log.type === "success" ? "success" : "info"}`}>  
            [{log.timestamp.toLocaleTimeString()}] {log.message}
          </div>
        ))}
      </div>
    </div>
  );
}