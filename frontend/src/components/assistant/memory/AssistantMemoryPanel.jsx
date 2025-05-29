import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import ReflectNowButton from "../ReflectNowButton";
import MemoryCard from "../../mcp_core/MemoryCard";

export default function AssistantMemoryPanel({ slug }) {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [project, setProject] = useState(null);
  const [visible, setVisible] = useState(25);
  const [meaningfulOnly, setMeaningfulOnly] = useState(false);

  useEffect(() => {
    if (!slug) return;
    async function load() {
      try {
        const [memRes, asst] = await Promise.all([
          apiFetch(`/assistants/${slug}/memories/`),
          apiFetch(`/assistants/${slug}/`),
        ]);
        setMemories(memRes || []);
        setVisible(25);
        setProject(asst.current_project || null);
      } catch (err) {
        console.error("Failed to fetch memories", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  if (loading) return <div>Loading memories...</div>;

  return (
    <div className="p-2 border rounded">
      <h5 className="mb-3">🧠 Recent Memories</h5>
      {project && (
        <div className="alert alert-secondary py-1 small">Project: {project.title}</div>
      )}
      <div className="form-check form-switch mb-2">
        <input
          className="form-check-input"
          type="checkbox"
          id="meaningfulOnly"
          checked={meaningfulOnly}
          onChange={(e) => setMeaningfulOnly(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="meaningfulOnly">
          Show Only Meaningful Memories ✅
        </label>
      </div>
      {memories.length === 0 ? (
        <div className="text-muted">No recent memories 📭</div>
      ) : (
        <ul className="list-group list-unstyled">
          {(meaningfulOnly ? memories.filter((m) => (m.summary || m.event || "").trim() !== "No meaningful content.") : memories)
            .slice(0, visible)
            .map((m) => (
            <li key={m.id} className="mb-2">
              <MemoryCard
                memory={m}
                action={<ReflectNowButton slug={slug} memoryId={m.id} />}
              />
            </li>
          ))}
        </ul>
      )}
      {visible < (meaningfulOnly ? memories.filter((m) => (m.summary || m.event || "").trim() !== "No meaningful content.").length : memories.length) && (
        <button className="btn btn-sm btn-outline-secondary mt-2" onClick={() => setVisible(visible + 25)}>
          Load More
        </button>
      )}
    </div>
  );
}
