import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import { reviewIngestDocument } from "../../../api/assistants";
import MemoryTimelinePanel from "../../../components/memory/MemoryTimelinePanel";

export default function ReviewIngestPage() {
  const { slug, doc_id } = useParams();
  const [assistant, setAssistant] = useState(null);
  const [doc, setDoc] = useState(null);
  const [summary, setSummary] = useState("");
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusMsg, setStatusMsg] = useState("");
  const [highlightId, setHighlightId] = useState(null);

  useEffect(() => {
    async function loadInfo() {
      if (!doc_id || doc_id === "undefined") {
        console.warn(
          `[ReviewIngest] Skipping doc fetch — invalid document ID: ${doc_id}`,
        );
        setLoading(false);
        return;
      }
      try {
        const [a, d] = await Promise.all([
          apiFetch(`/assistants/${slug}/`),
          apiFetch(`/intel/documents/${doc_id}/`),
        ]);
        setAssistant(a);
        setDoc(d);
      } catch (err) {
        console.error("Failed to load info", err);
      }
    }
    loadInfo();
  }, [slug, doc_id]);

  useEffect(() => {
    async function runReflection() {
      if (!doc_id || doc_id === "undefined") {
        console.warn(
          `[ReviewIngest] Skipping review — invalid document ID: ${doc_id}`,
        );
        return;
      }
      try {
        const res = await reviewIngestDocument(slug, doc_id);
        if (!res) throw new Error("review failed");
        if (res.status === "skipped") {
          console.warn(`[ReviewIngest] Reflection skipped: ${res.reason}`);
          if (res.reason && res.reason.toLowerCase().includes("chunk")) {
            try {
              const retry = await apiFetch(`/assistants/${slug}/reflect_again/?doc_id=${doc_id}`, {
                method: "POST",
              });
              if (retry?.results?.length > 0) {
                setSummary(retry.results[0].summary);
              }
            } catch (e) {
              console.error("Retry reflection failed", e);
            }
          }
        } else {
          setSummary(res.summary);
          const formatted = (res.insights || []).map((i) =>
            typeof i === "string" ? { text: i, tag: "" } : { text: i.text || "", tag: i.tag || "" }
          );
          setInsights(formatted);
        }
      } catch (err) {
        console.error("Reflection failed", err);
      } finally {
        setLoading(false);
      }
    }
    runReflection();
  }, [slug, doc_id]);

  const updateTag = (idx, value) => {
    setInsights((prev) => prev.map((ins, i) => (i === idx ? { ...ins, tag: value } : ins)));
  };

  const storeMemory = async (text) => {
    try {
      const res = await apiFetch("/memory/entries/", {
        method: "POST",
        body: { event: text, assistant: slug, document: doc_id, type: "ingest_insight" },
      });
      setStatusMsg("Memory stored!");
      setHighlightId(res.id);
    } catch (err) {
      console.error("Failed to store memory", err);
      setStatusMsg("Failed to store memory");
    }
  };

  const proposeAgent = async (text) => {
    try {
      await apiFetch("/agents/create-from-reflection/", {
        method: "POST",
        body: { assistant_id: slug, insight: text },
      });
      setStatusMsg("Agent proposal submitted!");
    } catch (err) {
      console.error("Failed to propose agent", err);
      setStatusMsg("Failed to propose agent");
    }
  };

  const archiveInsight = (idx) => {
    setInsights((prev) => prev.filter((_, i) => i !== idx));
    setStatusMsg("Insight archived");
  };

  if (loading)
    return (
      <div className="container my-5 text-center">
        <div className="spinner-border" role="status"></div>
        <p className="mt-3">Reflecting on document…</p>
      </div>
    );

  const topChunk = doc && doc.chunks && doc.chunks.length > 0 ? doc.chunks[0].text : "";

  return (
    <div className="container my-5">
      <h2 className="mb-3">Document Review</h2>
      {assistant && (
        <div className="d-flex align-items-center mb-3 gap-3">
          {assistant.avatar && (
            <img src={assistant.avatar} alt="avatar" width={48} height={48} className="rounded" />
          )}
          <div>
            <h5 className="mb-0">{assistant.name}</h5>
            {assistant.tone && (
              <small className="text-muted">Tone: {assistant.tone}</small>
            )}
          </div>
        </div>
      )}
      {doc && (
        <div className="mb-4">
          <h4 className="mb-1">{doc.title}</h4>
          <small className="text-muted">
            {doc.source_type} — {new Date(doc.created_at).toLocaleDateString()} • {doc.token_count} tokens
          </small>
        </div>
      )}
      {statusMsg && (
        <div className="alert alert-success" role="alert">
          {statusMsg}
        </div>
      )}

      {summary ? (
        <div className="alert alert-info">
          <strong>Summary:</strong> {summary}
        </div>
      ) : (
        topChunk && (
          <div className="alert alert-info">
            <strong>Top Chunk:</strong> {topChunk}
          </div>
        )
      )}

      {assistant && assistant.persona_summary && (
        <div className="alert alert-secondary">
          <strong>Here’s what I understood</strong>
          <p className="mb-0">{assistant.persona_summary}</p>
        </div>
      )}

      {insights.map((ins, idx) => (
        <div
          key={idx}
          className={`card mb-3 border-${
            ins.tag === "new_knowledge"
              ? "success"
              : ins.tag === "agent_proposal"
              ? "primary"
              : ins.tag === "irrelevant"
              ? "secondary"
              : "light"
          }`}
        >
          <div className="card-body">
            <p className="mb-2">{ins.text}</p>
            <div className="d-flex gap-2 flex-wrap">
              <select
                className="form-select form-select-sm w-auto"
                value={ins.tag}
                onChange={(e) => updateTag(idx, e.target.value)}
              >
                <option value="">Tag</option>
                <option value="new_knowledge">new_knowledge</option>
                <option value="agent_proposal">agent_proposal</option>
                <option value="irrelevant">irrelevant</option>
              </select>
              <button className="btn btn-sm btn-outline-secondary" disabled>
                🏷️ Add Tag
              </button>
              <button
                className="btn btn-sm btn-outline-success"
                onClick={() => storeMemory(ins.text)}
              >
                💾 Store as Memory
              </button>
              <button
                className="btn btn-sm btn-outline-primary"
                onClick={() => proposeAgent(ins.text)}
              >
                🤖 Propose Agent
              </button>
              <button
                className="btn btn-sm btn-outline-secondary"
                onClick={() => archiveInsight(idx)}
              >
                💃 Archive Insight
              </button>
            </div>
          </div>
        </div>
      ))}

      <MemoryTimelinePanel
        assistantId={slug}
        documentId={doc_id}
        highlightId={highlightId}
      />

      {import.meta.env.DEV && (
        <button
          className="btn btn-outline-warning me-2"
          onClick={async () => {
            const data = await reviewIngestDocument(slug, doc_id);
            console.log("[debug] reviewIngestDocument", data);
          }}
        >
          🐞 Test API
        </button>
      )}

      <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
        🔙 Back to Assistant
      </Link>
    </div>
  );
}
