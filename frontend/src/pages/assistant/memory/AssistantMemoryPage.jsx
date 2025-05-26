import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import MemoryCard from "../../../components/mcp_core/MemoryCard";

export default function AssistantMemoryPage() {
  const { slug } = useParams();
  const [tab, setTab] = useState("memories");
  const [memories, setMemories] = useState([]);
  const [reflections, setReflections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [mem, refl] = await Promise.all([
          apiFetch(`/assistants/${slug}/memories/`),
          apiFetch(`/assistants/${slug}/memories/?symbolic_change=true`),
        ]);
        setMemories(mem);
        setReflections(refl);
      } catch (err) {
        console.error("Failed to load memories", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  if (loading) return <div className="container my-5">Loading...</div>;

  const showReflections = reflections.length >= 3;

  const renderList = (items) => (
    <ul className="list-group mb-3">
      {items.map((m) => (
        <li key={m.id} className="list-group-item">
          <MemoryCard memory={m} />
        </li>
      ))}
    </ul>
  );

  return (
    <div className="container my-5">
      <h2 className="mb-3">Assistant Memory</h2>
      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "memories" ? "active" : ""}`}
            onClick={() => setTab("memories")}
          >
            Recent Memories
          </button>
        </li>
        {showReflections && (
          <li className="nav-item">
            <button
              className={`nav-link ${tab === "reflections" ? "active" : ""}`}
              onClick={() => setTab("reflections")}
            >
              🪞 Symbolic Reflections
            </button>
          </li>
        )}
      </ul>
      {tab === "memories" && renderList(memories)}
      {tab === "reflections" && renderList(reflections)}
      <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
        🔙 Back to Assistant
      </Link>
    </div>
  );
}
