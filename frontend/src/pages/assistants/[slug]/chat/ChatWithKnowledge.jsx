import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import { searchDocumentChunks, storeMemoryFromChat } from "../../../api/rag";

export default function ChatWithKnowledge() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/`)
      .then(setAssistant)
      .catch(() => {});
  }, [slug]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    const userMsg = { role: "user", content: input };
    try {
      const chunkRes = await searchDocumentChunks(input, slug);
      setChunks(chunkRes.results || []);
      const chatRes = await apiFetch(`/assistants/${slug}/chat/`, {
        method: "POST",
        body: { message: input },
      });
      const newMessages = [...messages, userMsg];
      if (chatRes.messages) {
        newMessages.push(...chatRes.messages);
      }
      setMessages(newMessages);
      setInput("");
    } catch (err) {
      setError("Failed to send message.");
    } finally {
      setLoading(false);
    }
  };

  const handleStore = async (content) => {
    try {
      await storeMemoryFromChat(content, ["chat", "rag"]);
      alert("Insight stored in memory.");
    } catch {
      alert("Failed to store memory");
    }
  };

  return (
    <div className="container my-4">
      <h1>
        💬 Chat with Knowledge: <span className="text-primary">{slug}</span>
      </h1>
      {assistant?.system_prompt && (
        <div className="alert alert-secondary small">
          {assistant.system_prompt.slice(0, 120)}...
        </div>
      )}
      <div className="d-flex">
        <div className="flex-grow-1">
          <div
            className="border rounded p-3 mb-3 bg-light"
            style={{ maxHeight: "400px", overflowY: "auto" }}
          >
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-3 ${msg.role === "user" ? "text-end" : "text-start"}`}
              >
                <span className={`badge ${msg.role === "user" ? "bg-primary" : "bg-secondary"}`}>{msg.role}</span>
                <div className="mt-1">{msg.content}</div>
                {msg.role === "assistant" && (
                  <button
                    className="btn btn-sm btn-outline-info mt-1"
                    onClick={() => handleStore(msg.content)}
                  >
                    🧠 Save Insight
                  </button>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={handleSend} className="d-flex gap-2">
            <input
              type="text"
              className="form-control"
              placeholder="Ask about the docs..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button className="btn btn-success" type="submit" disabled={loading}>
              {loading ? "Sending..." : "Send"}
            </button>
          </form>
          {error && <div className="alert alert-danger mt-2">{error}</div>}
        </div>
        {chunks.length > 0 && (
          <div
            className="ms-3 border rounded p-2 bg-white"
            style={{ width: "260px", maxHeight: "400px", overflowY: "auto" }}
          >
            <h6>Top Chunks</h6>
            {chunks.slice(0, 3).map((c, i) => (
              <div key={i} className="mb-2">
                <div className="small text-muted">{c.score?.toFixed(2)}</div>
                <div className="small">{(c.content || c.text).slice(0, 120)}...</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
