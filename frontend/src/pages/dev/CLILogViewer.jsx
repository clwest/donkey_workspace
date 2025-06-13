import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function CLILogViewer() {
  const { id } = useParams();
  const [log, setLog] = useState(null);

  useEffect(() => {
    apiFetch(`/dev/command-logs/${id}/`).then(setLog).catch(() => setLog(null));
  }, [id]);

  if (!log) return <div className="container">Loading...</div>;

  return (
    <div className="container my-4">
      <h3 className="mb-3">Command Log {id}</h3>
      <div className="mb-2">
        <strong>Command:</strong> {log.command}
      </div>
      <div className="mb-2">
        <strong>Status:</strong> {log.status}
      </div>
      <pre className="bg-light p-3">{log.output}</pre>
    </div>
  );
}
