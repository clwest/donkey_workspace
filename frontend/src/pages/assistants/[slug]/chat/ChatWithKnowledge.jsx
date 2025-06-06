import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../../../utils/apiClient";
import { searchDocumentChunks, storeMemoryFromChat } from "../../../../api/rag";
import AssistantBadgeIcon from "../../../../components/assistant/AssistantBadgeIcon";
import HintBubble from "../../../../components/HintBubble";
import useAssistantHints from "../../../../hooks/useAssistantHints";

export default function ChatWithKnowledge() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId] = useState(() => {
    const key = `chat_session_${slug}`;
    const stored = localStorage.getItem(key);
    if (stored) return stored;
    const id = crypto.randomUUID();
    localStorage.setItem(key, id);
    return id;
  });
  const cachedRef = useRef(null);
  const [showRestore, setShowRestore] = useState(false);
  const messagesEndRef = useRef(null);
  const { hints, dismissHint } = useAssistantHints(slug);
  const chatHint = hints.find((h) => h.id === "chat_welcome");
  const showChatWelcome = chatHint && !chatHint.dismissed;

  useEffect(() => {
    apiFetch(`/assistants/${slug}/`)
      .then(setAssistant)
      .catch(() => {});
  }, [slug]);

  useEffect(() => {
    const cached = localStorage.getItem(`chat_${slug}_${sessionId}`);
    if (cached) {
      cachedRef.current = JSON.parse(cached);
      setShowRestore(true);
      if (window.DEBUG_CHAT_CACHE) {
        console.log("Restoring chat:", cached);
      }
    }
  }, [slug, sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    return () => {
      localStorage.removeItem(`chat_${slug}_${sessionId}`);
      localStorage.removeItem(`chat_session_${slug}`);
    };
  }, [slug, sessionId]);

  useEffect(() => {
    if (messages.length) {
      localStorage.setItem(
        `chat_${slug}_${sessionId}`,
        JSON.stringify(messages)
      );
    }
  }, [messages, slug, sessionId]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    const userMsg = {
      role: "user",
      content: input,
      firstUser: messages.filter((m) => m.role === "user").length === 0,
    };
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
      if (showChatWelcome) {
        dismissHint("chat_welcome");
      }
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
        💬 Chat with Knowledge:
        <span className="text-primary"> {slug}</span>
        {assistant && (
          <AssistantBadgeIcon
            badges={assistant.skill_badges}
            primaryBadge={assistant.primary_badge}
          />
        )}
      </h1>
      {showRestore && (
        <div className="alert alert-warning d-flex justify-content-between align-items-center">
          <span>Restore previous chat?</span>
          <button
            className="btn btn-sm btn-primary"
            onClick={() => {
              setMessages(cachedRef.current || []);
              setShowRestore(false);
            }}
          >
            Restore
          </button>
        </div>
      )}
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
                {msg.firstUser && (
                  <span className="badge bg-info text-dark ms-2">🎯 First Impression</span>
                )}
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
          <div className="position-relative">
            {showChatWelcome && (
              <HintBubble
                label={chatHint.label}
                content={chatHint.content}
                highlightSelector="#knowledge-chat-input"
                position={{ top: -80 }}
                onDismiss={() => dismissHint("chat_welcome")}
              />
            )}
            <form onSubmit={handleSend} className="d-flex gap-2">
              <input
                id="knowledge-chat-input"
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
          </div>
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
