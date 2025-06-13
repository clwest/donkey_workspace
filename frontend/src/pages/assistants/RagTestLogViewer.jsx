import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function RagTestLogViewer() {
  useAuthGuard();
  const { slug } = useParams();
  const [logs, setLogs] = useState([]);
  const [file, setFile] = useState("");

  useEffect(() => {
    async function load() {
      const res = await apiFetch(`/assistants/${slug}/rag-tests/`);
      setLogs(res.logs || []);
      setFile(res.file);
    }
    load();
  }, [slug]);

  const parseResults = (output) => {
    return output
      .split("\n")
      .filter((l) => l.startsWith("["))
      .map((l) => {
        const m = l.match(/\[(\w+)\]\s*(.*)/);
        return m ? { status: m[1], text: m[2] } : null;
      })
      .filter(Boolean);
  };

  return (
    <div className="container my-4">
      <h3 className="mb-3">RAG Test Logs</h3>
      <div className="mb-2 text-muted">File: {file}</div>
      {logs.map((log) => (
        <div key={log.id} className="mb-4">
          <div className="fw-bold">{log.created_at}</div>
          <pre className="bg-light p-2">{log.command}</pre>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Result</th>
                <th>Question</th>
              </tr>
            </thead>
            <tbody>
              {parseResults(log.output).map((r, idx) => (
                <tr key={idx} className={r.status === "PASS" ? "table-success" : "table-danger"}>
                  <td>{r.status}</td>
                  <td className="text-break">{r.text}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
      {logs.length === 0 && <div>No logs found.</div>}
    </div>
  );
}
