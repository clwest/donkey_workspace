import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SymbolicMemorySynthesizer() {
  const [ids, setIds] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handle = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await apiFetch("/agents/memory/synthesize/", {
        method: "POST",
        body: { memory_ids: ids.split(",").map((s) => s.trim()) },
      });
      setResult(data);
    } catch (err) {
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-3 border rounded my-3">
      <h5>Symbolic Memory Synthesizer</h5>
      <form onSubmit={handle} className="mb-2">
        <input
          type="text"
          className="form-control mb-2"
          placeholder="Memory IDs comma separated"
          value={ids}
          onChange={(e) => setIds(e.target.value)}
        />
        <button className="btn btn-sm btn-primary" disabled={loading}>
          {loading ? "Synthesizing..." : "Synthesize"}
        </button>
      </form>
      {result && (
        <pre className="bg-light p-2 small">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
