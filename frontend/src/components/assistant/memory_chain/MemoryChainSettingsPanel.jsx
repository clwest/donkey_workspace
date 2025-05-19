import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function MemoryChainSettingsPanel({ slug, projectId }) {
  const [chain, setChain] = useState(null);
  const [memories, setMemories] = useState([]);

  useEffect(() => {
    async function load() {
      if (!projectId) return;
      const data = await apiFetch(`/assistants/projects/${projectId}/memory-chains/`);
      if (data.length > 0) {
        setChain(data[0]);
        const mem = await apiFetch(`/assistants/${slug}/memories/`);
        setMemories(mem.slice(0, 5));
      }
    }
    load();
  }, [projectId, slug]);

  const triggerReflection = async () => {
    if (!chain) return;
    await apiFetch(`/assistants/${slug}/reflect/chain/`, {
      method: "POST",
      body: { chain_id: chain.id },
    });
    alert("Reflection triggered");
  };

  if (!chain) return <div>No memory chain.</div>;

  return (
    <div className="border p-2 rounded mt-3">
      <h5>Memory Chain Settings</h5>
      <div className="mb-2">
        <label className="form-label">Mode</label>
        <select
          className="form-select"
          value={chain.mode}
          onChange={async (e) => {
            const updated = await apiFetch(`/assistants/memory-chains/${chain.id}/`, {
              method: "PATCH",
              body: { mode: e.target.value },
            });
            setChain(updated);
          }}
        >
          <option value="automatic">Automatic</option>
          <option value="manual">Manual</option>
        </select>
      </div>
      <button className="btn btn-sm btn-outline-secondary" onClick={triggerReflection}>
        Reflect Now
      </button>
      {memories.length > 0 && (
        <ul className="list-group mt-3">
          {memories.map((m) => (
            <li key={m.id} className="list-group-item">
              {m.event}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
