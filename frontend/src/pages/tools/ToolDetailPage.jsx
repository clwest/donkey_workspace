import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchTool, executeTool } from "../../api/tools";
import ToolLogsPanel from "../../components/tools/ToolLogsPanel";
import ToolReflectionsPanel from "../../components/tools/ToolReflectionsPanel";

export default function ToolDetailPage() {
  const { id } = useParams();
  const [tool, setTool] = useState(null);
  const [input, setInput] = useState("{}");
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState("run");

  useEffect(() => {
    if (!id) return;
    fetchTool(id).then(setTool).catch(() => setTool(null));
  }, [id]);

  const handleRun = async () => {
    try {
      const body = JSON.parse(input || "{}");
      const res = await executeTool(id, body);
      setResult(res);
    } catch (err) {
      console.error(err);
      setResult({ error: String(err) });
    }
  };

  if (!tool) return <div className="container">Loading...</div>;

  return (
    <div className="container mt-3">
      <h3>{tool.name}</h3>
      <p>{tool.description}</p>
      <ul className="nav nav-tabs mb-2">
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "run" ? "active" : ""}`}
            onClick={() => setTab("run")}
          >
            Run
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "logs" ? "active" : ""}`}
            onClick={() => setTab("logs")}
          >
            Logs
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "reflections" ? "active" : ""}`}
            onClick={() => setTab("reflections")}
          >
            Reflections
          </button>
        </li>
      </ul>
      {tab === "run" && (
        <div className="mb-3">
          <textarea
            className="form-control"
            rows="4"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="btn btn-primary mt-2" onClick={handleRun}>
            Run Tool
          </button>
          {result && (
            <pre className="bg-light p-2 border rounded mt-2">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
        </div>
      )}
      {tab === "logs" && <ToolLogsPanel toolId={id} />}
      {tab === "reflections" && <ToolReflectionsPanel toolId={id} />}
    </div>
  );
}
