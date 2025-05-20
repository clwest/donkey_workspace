import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import MemoryForkButton from "../../../components/memory/MemoryForkButton";
import "../styles/MemoryBrowserPage.css";

export default function MemoryBrowserPage() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scope, setScope] = useState("personal");

  useEffect(() => {
    async function fetchMemories() {
      try {
        const res = await fetch(
          `http://localhost:8000/api/memory/list/?scope=${scope}`
        );
        const data = await res.json();
        console.log(data)
        const grouped = {};
        for (const memory of data) {
          if (!memory.is_conversation || !memory.session_id) continue;

          if (!grouped[memory.session_id]) {
            grouped[memory.session_id] = [];
          }
          grouped[memory.session_id].push(memory);
        }

        const groupedConversations = Object.entries(grouped).map(
          ([sessionId, sessionMemories]) => ({
            session_id: sessionId,
            assistant: sessionMemories[0]?.linked_thought?.assistant_name ?? "Unknown",
            timestamp: sessionMemories[0]?.created_at,
            preview: sessionMemories[0]?.event,
            memory_ids: sessionMemories.map((m) => m.id),
          })
        );

        setConversations(groupedConversations);
      } catch (err) {
        console.error("Error loading memories", err);
      } finally {
        setLoading(false);
      }
    }

    fetchMemories();
  }, [scope]);

  if (loading) {
    return <div className="container my-5">Loading memories...</div>;
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4 display-5 fw-bold">🧠 Saved Conversations</h1>
      <div className="mb-3">
        <select
          className="form-select w-auto"
          value={scope}
          onChange={(e) => setScope(e.target.value)}
        >
          <option value="personal">Personal</option>
          <option value="team">Team</option>
          <option value="all">All</option>
        </select>
      </div>

      {conversations.length === 0 ? (
        <p className="text-muted">No memory conversations found. Start chatting with an assistant!</p>
      ) : (
        <div className="row g-4">
          {conversations.map((conv) => (
            <div className="col-md-6 col-lg-4" key={conv.session_id}>
              <Link to={`/memories/${conv.memory_ids[0]}`} className="text-decoration-none">
                <div className="card h-100 shadow-sm">
                  <div className="card-body">
                    <h6 className="card-subtitle text-muted mb-2">🤖 {conv.assistant}</h6>
                    <p className="card-text text-dark fw-semibold">
                      {conv.preview.length > 160 ? conv.preview.slice(0, 160) + "..." : conv.preview}
                    </p>
                    <small className="text-muted">
                      Saved {new Date(conv.timestamp).toLocaleDateString()}
                    </small>
                  </div>
                </div>
              </Link>
              <div className="mt-2">
                <MemoryForkButton memoryId={conv.memory_ids[0]} />
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-5">
        <Link to="/memories/reflect" className="btn btn-outline-info btn-lg">
          ✨ Reflect on Memories
        </Link>
      </div>
    </div>
  );
}