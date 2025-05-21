import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LoreTokenCreator({ assistantId }) {
  const [ids, setIds] = useState("");
  const [token, setToken] = useState(null);
  const [creating, setCreating] = useState(false);

  async function createToken() {
    setCreating(true);
    try {
      const memory_ids = ids.split(',').map((s) => s.trim()).filter(Boolean);
      const data = await apiFetch("/lore-tokens/", {
        method: "POST",
        body: { memory_ids, assistant: assistantId },
      });
      setToken(data);
    } catch (err) {
      console.error("Failed to create token", err);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="my-3">
      <h5>Create Lore Token</h5>
      <textarea
        className="form-control"
        rows="2"
        value={ids}
        onChange={(e) => setIds(e.target.value)}
        placeholder="Memory IDs comma separated"
      />
      <button className="btn btn-primary mt-2" onClick={createToken} disabled={creating}>
        Compress Memories
      </button>
      {token && (
        <pre className="bg-light p-2 mt-2 border rounded" style={{ whiteSpace: "pre-wrap" }}>
          {token.summary}
        </pre>
      )}
    </div>
  );
}
