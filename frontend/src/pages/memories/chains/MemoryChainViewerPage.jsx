import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

export default function MemoryChainViewerPage() {
  const { id } = useParams();
  const [chain, setChain] = useState(null);

  useEffect(() => {
    async function fetchChain() {
      const res = await fetch(`http://localhost:8000/api/memory/chains/${id}/`);
      const data = await res.json();
      setChain(data);
    }
    fetchChain();
  }, [id]);

  if (!chain) return <div className="container my-5">Loading chain...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🔗 {chain.title}</h1>

      <div className="list-group mb-4">
        {chain.memories.map(memory => (
          <div key={memory.id} className="list-group-item">
            <strong>{new Date(chain.created_at).toLocaleDateString()}:</strong>
            <p>{memory.event}</p>
            {memory.emotion && (
              <span className="badge bg-info text-dark">{memory.emotion}</span>
            )}
          </div>
        ))}
      </div>

      <Link to="/memories" className="btn btn-secondary">
        ⬅️ Back to Memories
      </Link>
    </div>
  );
}