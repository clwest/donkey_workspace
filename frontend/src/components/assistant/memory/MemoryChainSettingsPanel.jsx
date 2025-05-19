import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import ReflectNowButton from "../ReflectNowButton";

export default function MemoryChainSettingsPanel({ slug }) {
  const [chain, setChain] = useState(null);
  const [memories, setMemories] = useState([]);

  useEffect(() => {
    async function load() {
      const asst = await apiFetch(`/assistants/${slug}/`);
      if (!asst.current_project) return;
      const chains = await apiFetch(
        `/assistants/projects/${asst.current_project.id}/memory-chains/`
      );
      if (chains.length > 0) setChain(chains[0]);
      const mems = await apiFetch(`/assistants/${slug}/memories/`);
      setMemories(mems);
    }
    load();
  }, [slug]);

  if (!chain) return <div>No memory chain configured.</div>;

  const filtered = memories
    .filter((m) =>
      chain.filter_tags.length === 0
        ? true
        : m.tags.some((t) =>
            chain.filter_tags.find((ft) => ft.id === t.id)
          )
    )
    .filter((m) =>
      chain.exclude_types.length === 0
        ? true
        : !chain.exclude_types.includes(m.type)
    )
    .slice(0, 5);

  return (
    <div className="p-2 border rounded mt-3">
      <h5 className="mb-2">Memory Chain Settings</h5>
      <div className="mb-2">
        <strong>Mode:</strong> {chain.mode}
      </div>
      {chain.filter_tags.length > 0 && (
        <div className="mb-2">
          <strong>Tags:</strong>{" "}
          {chain.filter_tags.map((t) => `#${t.name}`).join(", ")}
        </div>
      )}
      {chain.exclude_types.length > 0 && (
        <div className="mb-2">
          <strong>Exclude Types:</strong> {chain.exclude_types.join(", ")}
        </div>
      )}
      <ReflectNowButton slug={slug} projectId={chain.project} />
      {filtered.length > 0 && (
        <ul className="list-group mt-3">
          {filtered.map((m) => (
            <li key={m.id} className="list-group-item">
              {m.summary || m.event}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
