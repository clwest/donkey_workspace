import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PromptDebuggerPage() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/debug/prompts/")
      .then((res) => setLogs(res.results || res))
      .catch((err) => console.error("Failed to load prompt logs", err));
  }, []);

  return (
    <div className="container my-4">
      <h3>Prompt Debugger</h3>
      <pre>{JSON.stringify(logs, null, 2)}</pre>
    </div>
  );
}
