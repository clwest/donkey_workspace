import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function MemoryChainDetailPage() {
  const { id } = useParams();
  const [chain, setChain] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchChain() {
      const data = await apiFetch(`/memory/chain/${id}/`);
      setChain(data);

      setLoading(false);
    }
    fetchChain();
  }, [id]);

  if (loading) return <div className="container my-5">Loading chain...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🔗 {chain.title}</h1>

      <div className="list-group">
        {chain.memories.map((memory) => (
          <Link
            key={memory.id}
            to={`/memories/${memory.id}`}
            className="list-group-item list-group-item-action"
          >
            {memory.event.slice(0, 100)}...
          </Link>
        ))}
      </div>

      <div className="mt-4">
        <Link to="/memories" className="btn btn-secondary">
          🔙 Back to Memories
        </Link>
      </div>
    </div>
  );
}