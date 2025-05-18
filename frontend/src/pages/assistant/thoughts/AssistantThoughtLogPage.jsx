import { useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";

export default function AssistantThoughtLogPage() {
  const { slug } = useParams();
  const [thought, setThought] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogThought = async () => {
    if (!thought.trim()) return;

    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/assistants/${slug}/log_thought/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thought }), // ✅ renamed from "message"
      });

      const data = await res.json();
      if (res.ok) {
        setResponse(data.thought);
        toast.success("🧠 Thought logged!");
        setThought(""); // optional: clear textarea
      } else {
        toast.error("💥 Assistant failed to log the thought.");
      }
    } catch (err) {
      toast.error("⚠️ Error logging thought.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Log a Thought</h1>

      <textarea
        className="form-control mb-3"
        rows={3}
        value={thought}
        onChange={(e) => setThought(e.target.value)}
        placeholder="What do you want the assistant to log as a thought?"
      />

      <button className="btn btn-primary mb-3" onClick={handleLogThought} disabled={loading}>
        {loading ? "Logging..." : "💾 Log Thought"}
      </button>

      {response && (
        <div className="alert alert-info">
          <strong>Logged Thought:</strong>
          <div className="mt-2">{response}</div>
        </div>
      )}
    </div>
  );
}