import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import useAssistantMemories from "../../../hooks/useAssistantMemories";
import ReflectNowButton from "../ReflectNowButton";
import MemoryCard from "../../mcp_core/MemoryCard";

export default function AssistantMemoryPanel({ slug, refreshKey = 0 }) {
  const { memories, loading, refresh } = useAssistantMemories(slug, { limit: 100 });
  const [project, setProject] = useState(null);
  const [visible, setVisible] = useState(10);
  const [showAll, setShowAll] = useState(false);
  const [tagFilter, setTagFilter] = useState("");
  const [meaningfulOnly, setMeaningfulOnly] = useState(true);

  const isWeak = (m) => (m.token_count || 0) < 5 && (m.importance || 0) <= 2;

  useEffect(() => {
    if (!slug) return;
    async function load() {
      try {
        const asst = await apiFetch(`/assistants/${slug}/`);
        setProject(asst.current_project || null);
        setVisible(10);
        setShowAll(false);
        setTagFilter("");
      } catch (err) {
        console.error("Failed to fetch assistant", err);
      }
    }
    load();
  }, [slug]);

  useEffect(() => {
    refresh();
  }, [refreshKey]);

  if (loading)
    return (
      <div className="placeholder-glow">
        <div className="placeholder col-12 mb-2" style={{ height: 20 }}></div>
        <div className="placeholder col-8" style={{ height: 20 }}></div>
      </div>
    );

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
        <>
          <div className="d-flex mb-2 align-items-center gap-2">
            <select
              className="form-select form-select-sm"
              style={{ maxWidth: "160px" }}
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
            >
              <option value="">All Tags</option>
              <option value="delegation">#delegation</option>
              <option value="reflection">#reflection</option>
            </select>
            <div className="form-check ms-2">
              <input
                className="form-check-input"
                type="checkbox"
                id="showAll"
                checked={showAll}
                onChange={(e) => setShowAll(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="showAll">
                Show All
              </label>
            </div>
          </div>
          <ul className="list-group list-unstyled">
            {memories
              .filter((m) => !meaningfulOnly || !isWeak(m))
              .filter(
                (m) =>
                  !tagFilter ||
                  (m.tags || []).some((t) =>
                    t.name.toLowerCase().includes(tagFilter)
                  )
              )
              .slice(0, showAll ? memories.length : visible)
              .map((m) => (
                <li key={m.id} className="mb-2">
                  <MemoryCard
                    memory={m}
                    action={<ReflectNowButton slug={slug} memoryId={m.id} />}
                  />
                </li>
              ))}
          </ul>
        </>
      )}
    </div>
  );
}
