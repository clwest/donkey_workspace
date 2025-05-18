import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import AssistantThinkButton from "../../../components/assistant/thoughts/AssistantThinkButton";
import AssistantThoughtCard from "../../../components/assistant/thoughts/AssistantThoughtCard";

// import "./styles/AssistantThought.css"

export default function AssistantThoughtsPage() {
  const [thoughts, setThoughts] = useState([]);
  const [viewAll, setViewAll] = useState({})  
  const { slug } = useParams();

  useEffect(() => {
    if (!slug) return;

    const fetchThoughts = async () => {
      try {
        const data = await fetch(`/api/assistants/${slug}/thoughts/`);
        // const data = await res.json();
        console.log(data)
        const thoughtsList = Array.isArray(data) ? data : data.results;
        if (Array.isArray(thoughtsList)) {
          setThoughts(thoughtsList.reverse());
        }
      } catch (err) {
        console.error("Error fetching thoughts:", err);
      }
    };

    fetchThoughts();
  }, [slug]);

  const getThoughtsByType = (type) =>
    thoughts.filter((t) => t.thought_type === type || (type === "cot" && t.thought_trace?.includes("🧩")));

const MAX_VISIBLE = 6;

const toggleView = (type) => {
  setViewAll((prev) => ({ ...prev, [type]: !prev[type] }));
};

const renderSection = (title, icon, type, color) => {
  const sectionThoughts = getThoughtsByType(type);
  if (!sectionThoughts || sectionThoughts.length === 0) return null;

  const showingAll = viewAll[type];
  const displayed = showingAll ? sectionThoughts : sectionThoughts.slice(0, 6);

  return (
    <div className="mb-5">
      <h5 className={`mb-3 text-${color}`}>
        {icon} {title} ({sectionThoughts.length})
      </h5>
      <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
        {displayed.map((t) => (
          <div className="col" key={t.id}>
            <AssistantThoughtCard
              thought={t}
              badge={title}
              color={color}
              icon={icon}
            />
          </div>
        ))}
      </div>

      {sectionThoughts.length > 6 && (
        <div className="text-center mt-3">
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={() => toggleView(type)}
          >
            {showingAll ? "⬆️ Show Less" : "🔽 View All"}
          </button>
        </div>
      )}
    </div>
  );
};

  return (
    <div className="container my-5">
      <h2 className="mb-4">
        🧠 Thoughts for Assistant: <span className="text-primary">{slug}</span>
      </h2>

      <div className="mb-4">
        <Link to={`/assistants/${slug}/chat`} className="btn btn-outline-secondary">
          💬 Chat with Assistant
        </Link>
        <AssistantThinkButton slug={slug} />
      </div>

      {renderSection("User Thought", "👤", "user", "danger")}
      {renderSection("Chain of Thought", "🧩", "cot", "warning")}
      {renderSection("Generated Thought", "🤖", "generated", "primary")}
      {renderSection("Planning", "🛠️", "planning", "info")}
      {renderSection("Reflection", "🪞", "reflection", "secondary")}
    </div>
  );
}