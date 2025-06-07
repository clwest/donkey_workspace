import { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import TagBadge from "../../../components/TagBadge";
import HintBubble from "../../../components/HintBubble";
import useAssistantHints from "../../../hooks/useAssistantHints";
import { suggestAssistant, suggestSwitch, switchAssistant } from "../../../api/assistants";

const AVATAR_EMOJI = {
  owl: "🦚",
  fox: "🦊",
  robot: "🤖",
  wizard: "🧙‍♂️",
};
import "./styles/ChatView.css";
import ChatDebugPanel from "../../../components/assistant/ChatDebugPanel";

import useGlossaryOverlay from "../../../hooks/glossary";
import GlossaryOverlayTooltip from "../../../components/GlossaryOverlayTooltip";


export default function ChatWithAssistantPage() {
  const { slug } = useParams();
  const [messages, setMessages] = useState([]);
  const [assistantInfo, setAssistantInfo] = useState(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [switchSuggestion, setSwitchSuggestion] = useState(null);
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
  const [sourceInfo, setSourceInfo] = useState(null);
  const [glossarySuggestion, setGlossarySuggestion] = useState(null);
  const [focusOnly, setFocusOnly] = useState(true);
  const [noContextMatch, setNoContextMatch] = useState(false);
  const [contextScore, setContextScore] = useState(null);
  const [glossaryWarning, setGlossaryWarning] = useState(null);
  const [anchorWarning, setAnchorWarning] = useState(null);
  const [primerDone, setPrimerDone] = useState(
    !!localStorage.getItem(`primer_done_${slug}`)
  );
  const { hints, dismissHint } = useAssistantHints(slug);
  const chatHint = hints.find((h) => h.id === "chat_welcome");
  const showChatWelcome = chatHint && !chatHint.dismissed;
  const glossaryOverlays = useGlossaryOverlay('chat');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/`)
      .then(setAssistantInfo)
      .catch(() => {});
  }, [slug]);

  useEffect(() => {
    if (messages.length) {
      localStorage.setItem(
        `chat_${slug}_${sessionId}`,
        JSON.stringify(messages)
      );
    }
  }, [messages, slug, sessionId]);

  // Load cached messages on mount
  useEffect(() => {
    const cached = localStorage.getItem(`chat_${slug}_${sessionId}`);
    if (cached) {
      cachedRef.current = JSON.parse(cached);
      setShowRestore(true);
      if (window.DEBUG_CHAT_CACHE) {
        console.log("Restoring chat:", cached);
      }
    } else {
      const fetchSession = async () => {
        const data = await apiFetch(`/assistants/${slug}/chat/`, {
          method: "POST",
          body: { message: "__ping__", session_id: sessionId },
        });
        setMessages(data.messages || []);
      };
      fetchSession();
    }
  }, [slug, sessionId]);

  useEffect(() => {
    return () => {
      localStorage.removeItem(`chat_${slug}_${sessionId}`);
      localStorage.removeItem(`chat_session_${slug}`);
    };
  }, [slug, sessionId]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const data = await apiFetch(`/assistants/${slug}/chat/`, {
        method: "POST",
        body: { message: input, session_id: sessionId, focus_only: focusOnly },
      });
      const msgs = data.messages || [];
      if (msgs.length && data.rag_meta) {
        const last = msgs[msgs.length - 1];
        if (last.role === "assistant") {
          last.rag_used = data.rag_meta.rag_used;
          last.used_chunks = data.rag_meta.used_chunks || [];
          last.rag_ignored_reason = data.rag_meta.rag_ignored_reason;
          last.rag_fallback = data.rag_meta.rag_fallback;
          last.glossary_present = data.rag_meta.glossary_present;
          last.glossary_used = data.rag_meta.glossary_used;
          last.glossary_retry_id = data.rag_meta.glossary_retry_id;
          last.glossary_retry_score_diff = data.rag_meta.score_diff;
          last.context_score = data.rag_meta.used_chunks?.[0]?.score || null;
        }
        const topScore = data.rag_meta.used_chunks?.[0]?.score || null;
        setContextScore(topScore);
        setNoContextMatch(!(data.rag_meta.used_chunks?.length > 0));
        if (!data.rag_meta.glossary_present) {
          setGlossaryWarning(
            "No glossary loaded. Glossary terms improve retrieval accuracy."
          );
        } else {
          setGlossaryWarning(null);
        }
        if (!data.rag_meta.anchors || data.rag_meta.anchors.length === 0) {
          setAnchorWarning(
            "You can define anchors to help assistants recognize key concepts."
          );
        } else {
          setAnchorWarning(null);
        }
        setSourceInfo(data.rag_meta);
        if (data.rag_meta.glossary_present && !data.rag_meta.rag_used) {
          setGlossarySuggestion(
            "Try asking: 'What does MCP mean in this document?' or 'Summarize this glossary.'"
          );
        } else {
          setGlossarySuggestion(null);
        }
      }
      const first = messages.filter((m) => m.role === "user").length === 0;
      if (first && msgs.length) {
        const userIndex = msgs.findIndex((m) => m.role === "user");
        if (userIndex >= 0) msgs[userIndex].firstUser = true;
      }
      setMessages(msgs);
      console.log(data);
      setInput("");
      if (showChatWelcome) {
        dismissHint("chat_welcome");
      }

      const userCount = msgs.filter((m) => m.role === "user").length;
      if (!primerDone && userCount >= 3) {
        try {
          const res = await apiFetch(`/assistants/${slug}/reflect_first_use/`, {
            method: "POST",
          });
          toast.info(res.summary || "Reflection generated");
          setPrimerDone(true);
          localStorage.setItem(`primer_done_${slug}`, "1");
        } catch (err) {
          console.error("Failed to run first reflection", err);
        }
      }
    } catch (err) {
      setError("⚠️ Failed to send message.");
    } finally {
      setLoading(false);
    }
  };


  const handleSuggest = async () => {
    try {
      const summary = messages.map((m) => m.content).join(" ");
      const data = await suggestAssistant({
        context_summary: summary.slice(-500),
        tags: [],
        recent_messages: messages.slice(-5),
      });
      if (data.suggested_assistant) {
        alert(`Try: ${data.suggested_assistant.name}\nReason: ${data.reasoning}`);
      } else {
        alert("No suggestion available");
      }
    } catch (err) {
      alert("Failed to get suggestion");
    }
  };

  const handleSwitchSuggest = async () => {
    try {
      const data = await suggestSwitch(sessionId);
      if (data.suggested_assistant) {
        const a = data.suggested_assistant;
        if (window.confirm(`Switch to ${a.name}?\nReason: ${a.reason}`)) {
          const res = await switchAssistant(sessionId, a.slug);
          window.location.href = `/assistants/${a.slug}/chat/`;
        }
      } else {
        alert("No switch suggested");
      }
    } catch (err) {
      alert("Failed to suggest switch");
    }
  };

  const handleCheckSource = async (text) => {
    try {
      const data = await apiFetch("/rag/check-source/", {
        method: "POST",
        body: { assistant_id: slug, content: text, mode: "response" },
      });
      if (data.results && data.results.length > 0) {
        const lines = data.results.slice(0, 3).map((c, i) => {
          const score = c.score || c.similarity_score || 0;
          const warn = c.embedding_status && c.embedding_status !== "embedded" ? " ⚠️" : "";
          return `${i + 1}. ${c.chunk_id || c.id} | ${score.toFixed(2)} | ${c.text.slice(0, 80)}${warn}`;
        });
        let note = "";
        const bestScore = data.results[0].score || data.results[0].similarity_score || 0;
        if (bestScore < 0.3) note = "\n⚠️ Using fallback due to low score";
        if (data.results.some((c) => c.embedding_status && c.embedding_status !== "embedded")) {
          note += "\n⚠️ Some matches are unembedded. RAG accuracy may be degraded.";
        }
        alert(lines.join("\n") + note);
      } else {
        alert("No matching source chunk found.");
      }
    } catch (err) {
      alert("Failed to check source");
    }
  };

  return (
    <div className="container my-5">
      <h1>
        {AVATAR_EMOJI[assistantInfo?.avatar_style] || "🤖"} Chat with Assistant:
        <span className="text-primary ms-1">{slug}</span>
      </h1>
      <div className="mb-2">
        {glossaryOverlays.map((o) => (
          <GlossaryOverlayTooltip key={o.slug} {...o} />
        ))}
      </div>

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

      {noContextMatch && (
        <div className="alert alert-warning mt-3">
          ⚠️ No strong matches found. Assistant is replying without confirmed context.
        </div>
      )}
      {glossaryWarning && (
        <div className="alert alert-info mt-2">{glossaryWarning}</div>
      )}
      {anchorWarning && (
        <div className="alert alert-info mt-2">{anchorWarning}</div>
      )}

      <div className="chat-box border rounded p-3 mb-4 bg-light" style={{ maxHeight: "500px", overflowY: "auto" }}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-4 ${msg.role === "user" ? "text-end" : "text-start"}`}>
          <div className="d-flex justify-content-between">
            <span className={`badge ${msg.role === "user" ? "bg-primary" : "bg-secondary"}`}>
              {msg.role}
            </span>
            {msg.firstUser && (
              <span className="badge bg-info text-dark ms-2">🎯 First Impression</span>
            )}
            <small className="text-muted ms-2">{new Date(msg.timestamp).toLocaleString()}</small>
          </div>

            <div className="mt-2 text-break">
              {msg.content?.split("\n").map((line, i) =>
                line.trim() === "" ? <br key={i} /> : <p key={i} className="mb-1">{line}</p>
              )}
            </div>

            {msg.tags?.length > 0 && (
              <div className="mt-1">
                {msg.tags.map((tag, i) => {
                  if (typeof tag === "string") {
                    return (
                      <span
                        key={i}
                        className="badge rounded-pill bg-info text-dark me-1"
                      >
                        #{tag}
                      </span>
                    );
                  }
                  return <TagBadge key={tag.id || tag.slug || i} tag={tag} />;
                })}
              </div>
            )}

            {msg.role === "assistant" && (
              <div className="mt-1">
                {msg.rag_fallback && (msg.used_chunks?.[0]?.score || 0) < 0.6 ? (
                  <span className="badge bg-warning text-dark">⚠️ Weak Context</span>
                ) : msg.rag_used ? (
                  (msg.used_chunks?.[0]?.score || 0) >= 0.75 ? (
                    <span className="badge bg-success">🔗 Good Source</span>
                  ) : null
                ) : (
                  <span className="badge bg-danger">🚫 No Source Used</span>
                )}
              </div>
            )}

            <button
              className="btn btn-sm btn-outline-info mt-1"
              onClick={() => handleCheckSource(msg.content)}
            >
              📄 Check Source
            </button>
            {msg.role === "assistant" && msg.context_score != null && (
              <span className="badge bg-secondary ms-2" title="Top context score">
                Context Score: {msg.context_score.toFixed(4)}
                {msg.context_score < 0.65 ? " (weak)" : ""}
              </span>
            )}

            {msg.memory_id && (
              <div className="mt-2">
                <Link to={`/memory/${msg.memory_id}`} className="btn btn-sm btn-outline-dark">
                  🧠 View Memory
                </Link>
              </div>
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
            highlightSelector="#chat-input"
            position={{ top: -80 }}
            onDismiss={() => dismissHint("chat_welcome")}
          />
        )}
        <form onSubmit={handleSend} className="d-flex gap-2">
          <input
            id="chat-input"
            type="text"
            className="form-control"
            placeholder="Ask something..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button className="btn btn-success" type="submit" disabled={loading}>
            {loading ? "Thinking..." : "Send"}
          </button>
        </form>
      </div>
      <div className="form-check form-switch mt-2">
        <input
          className="form-check-input"
          type="checkbox"
          id="focusOnlyToggle"
          checked={focusOnly}
          onChange={(e) => setFocusOnly(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="focusOnlyToggle">
          Focus Anchors Only
        </label>
      </div>
      {sourceInfo && (
        <div className="mt-2">
          {sourceInfo.rag_fallback &&
          (sourceInfo.used_chunks?.[0]?.score || 0) < 0.6 ? (
            <span className="badge bg-warning text-dark">⚠️ Weak Context</span>
          ) : sourceInfo.rag_used ? (
            (sourceInfo.used_chunks?.[0]?.score || 0) >= 0.75 ? (
              <span className="badge bg-success">🔗 Good Source</span>
            ) : null
          ) : (
            <span className="badge bg-danger">🚫 No Source Used</span>
          )}
          {" "}
          {sourceInfo.glossary_present && !sourceInfo.rag_used ? (
            <span className="badge bg-warning text-dark">⚠️ Ignored Glossary</span>
          ) : (
            <span className="badge bg-secondary">
              📘 Glossary Present: {sourceInfo.glossary_present ? "✅" : "❌"}
            </span>
          )}
          {sourceInfo.prompt_appended_glossary && (
            <span className="badge bg-info text-dark ms-2">✅ Guidance Appended</span>
          )}
          {sourceInfo.guidance_appended &&
            sourceInfo.glossary_ignored?.length > 0 && (
              <span className="badge bg-danger ms-2">🚨 Glossary Ignored</span>
            )}
          {sourceInfo.escalated_retry && (
            <span className="badge bg-info text-dark ms-2">🔁 Escalated Retry Used</span>
          )}
          {sourceInfo.glossary_retry_id && (
            <a
              href={`/memory/glossary-retries/${sourceInfo.glossary_retry_id}`}
              className="badge bg-info text-dark ms-2"
              title="Initial reply ignored glossary context. LLM was retried using explicit guidance."
            >
              🔄 Glossary Retry
              {sourceInfo.glossary_retry_score_diff > 0 && (
                <span className="ms-1 text-success">+{sourceInfo.glossary_retry_score_diff}</span>
              )}
            </a>
          )}
        </div>
      )}
      <button className="btn btn-outline-primary mt-2" onClick={handleSuggest}>
        🤖 Suggest Assistant
      </button>
      <button className="btn btn-outline-warning mt-2 ms-2" onClick={handleSwitchSuggest}>
        🔄 Suggest Switch
      </button>
      {glossarySuggestion && (
        <div className="alert alert-info mt-3">{glossarySuggestion}</div>
      )}

      {sourceInfo && (
        <div className="mt-3 small border-top pt-2">
          <h6>Debug</h6>
          <ul className="list-unstyled">
            <li>📚 Source Used: {sourceInfo.rag_used ? "✅" : "❌"}</li>
            <li>🧠 Glossary Present: {sourceInfo.glossary_present ? "✅" : "❌"}</li>
            <li>🧷 Symbolic Anchors: {JSON.stringify(sourceInfo.anchors || [])}</li>
            <li>✅ Anchor Hits: {JSON.stringify(sourceInfo.anchor_hits || [])}</li>
            <li>❌ Anchor Misses: {JSON.stringify(sourceInfo.anchor_misses || [])}</li>
            <li>📎 Chunk Match Scores: {JSON.stringify(sourceInfo.chunk_scores || [])}</li>
            <li>🔍 Filtered Anchors: {JSON.stringify(sourceInfo.filtered_anchor_terms || [])}</li>
            <li>📓 Glossary Chunk IDs: {JSON.stringify(sourceInfo.glossary_chunk_ids || [])}</li>
          <li>
              📄 Used Chunks:
              {sourceInfo.used_chunks?.map((c) => (
                <div key={c.chunk_id}>
                  <span className="badge bg-secondary me-1">{c.chunk_id}</span>
                  {c.anchor_slug && (
                    <span className="badge bg-info text-dark me-1">{c.anchor_slug}</span>
                  )}
                  {c.anchor_confidence !== undefined && (
                    <span className="badge bg-light text-dark me-1">
                      {c.anchor_confidence.toFixed(1)}
                    </span>
                  )}
                  {c.override_reason === "anchor-match" && (
                    <span
                      className="badge bg-warning text-dark me-1"
                      title="This chunk was included due to a glossary match even though its vector score was low."
                    >
                      Glossary Anchor Override
                    </span>
                  )}
                  {c.text ? c.text.slice(0, 30) : ""}
                </div>
              ))}
          </li>
          {sourceInfo.used_chunks?.some((c) => c.embedding_status !== "embedded") && (
            <div className="alert alert-danger mt-2">
              Some chunks have invalid embedding status
            </div>
          )}
            {sourceInfo.glossary_definitions?.length > 0 && (
              <li>
                🧠 Glossary Definition Injected: "{sourceInfo.glossary_definitions[0]}"
              </li>
            )}
            {sourceInfo.glossary_guidance?.length > 0 && (
              <li>
                📝 Anchor Guidance: {sourceInfo.glossary_guidance.join(" | ")}
              </li>
            )}
            {sourceInfo.prompt_appended_glossary && (
              <li>✅ Guidance Appended</li>
            )}
            {sourceInfo.guidance_appended && sourceInfo.glossary_ignored?.length > 0 && (
              <li className="text-danger">
                🚨 Glossary Ignored: {JSON.stringify(sourceInfo.glossary_ignored)}
              </li>
            )}
            {sourceInfo.escalated_retry && (
              <li>🔁 Escalated Retry Used</li>
            )}
          </ul>
          {sourceInfo.glossary_ignored?.length > 0 && (
            <div className="alert alert-warning mt-2">
              ⚠️ Consider retry with anchor guidance emphasis
            </div>
          )}
        </div>
      )}

      {sourceInfo && <ChatDebugPanel ragMeta={sourceInfo} slug={slug} />}

      {error && <div className="alert alert-danger mt-3">{error}</div>}
    </div>
  );
}