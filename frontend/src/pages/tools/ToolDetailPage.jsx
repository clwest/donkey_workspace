import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchTool, executeTool } from "../../api/tools";
import ToolLogsPanel from "../../components/tools/ToolLogsPanel";

export default function ToolDetailPage() {
  const { id } = useParams();
  const [tool, setTool] = useState(null);
  const [input, setInput] = useState("{}");
  const [result, setResult] = useState(null);

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
      </div>
      {result && (
        <pre className="bg-light p-2 border rounded">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
      <ToolLogsPanel toolId={id} />
    </div>
  );
}
