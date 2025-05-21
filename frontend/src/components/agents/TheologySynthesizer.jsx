import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function TheologySynthesizer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await apiFetch("/agents/theology/synthesize/", {
        method: "POST",
        body: { text },
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
      <h5>Theology Synthesizer</h5>
      <form onSubmit={handleSubmit}>
        <textarea
          className="form-control mb-2"
          rows="3"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button className="btn btn-sm btn-primary" disabled={loading}>
          {loading ? "Synthesizing..." : "Synthesize"}
        </button>
      </form>
      {result && (
        <pre className="mt-3 bg-light p-2 small">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
