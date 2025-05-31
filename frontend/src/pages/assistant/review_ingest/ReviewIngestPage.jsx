import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function ReviewIngestPage() {
  const { id, doc_id } = useParams();
  const [assistant, setAssistant] = useState(null);
  const [doc, setDoc] = useState(null);
  const [summary, setSummary] = useState("");
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInfo() {
      try {
        const [a, d] = await Promise.all([
          apiFetch(`/assistants/${id}/`),
          apiFetch(`/intel/documents/${doc_id}/`),
        ]);
        setAssistant(a);
        setDoc(d);
      } catch (err) {
        console.error("Failed to load info", err);
      }
    }
    loadInfo();
  }, [id, doc_id]);

  useEffect(() => {
    async function runReflection() {
      try {
        const res = await apiFetch(
          `/assistants/${id}/review-ingest/${doc_id}/`,
          { method: "POST" }
        );
        setSummary(res.summary);
        const formatted = (res.insights || []).map((i) =>
          typeof i === "string" ? { text: i, tag: "" } : { text: i.text || "", tag: i.tag || "" }
        );
        setInsights(formatted);
      } catch (err) {
        console.error("Reflection failed", err);
      } finally {
        setLoading(false);
      }
    }
    runReflection();
  }, [id, doc_id]);

  const updateTag = (idx, value) => {
    setInsights((prev) => prev.map((ins, i) => (i === idx ? { ...ins, tag: value } : ins)));
  };

  const storeMemory = async (text) => {
    try {
      await apiFetch("/memory/entries/", {
        method: "POST",
        body: { event: text, assistant: id, document: doc_id, type: "ingest_insight" },
      });
    } catch (err) {
      console.error("Failed to store memory", err);
    }
  };

  const proposeAgent = async (text) => {
    try {
      await apiFetch("/agents/create-from-reflection/", {
        method: "POST",
        body: { assistant_id: id, insight: text },
      });
    } catch (err) {
      console.error("Failed to propose agent", err);
    }
  };

  const archiveInsight = (idx) => {
    setInsights((prev) => prev.filter((_, i) => i !== idx));
  };

  if (loading) return <div className="container my-5">Loading...</div>;

  const topChunk = doc && doc.chunks && doc.chunks.length > 0 ? doc.chunks[0].text : "";

  return (
    <div className="container my-5">
      <h2 className="mb-3">Document Review</h2>
      {doc && (
        <div className="mb-4">
          <h4 className="mb-1">{doc.title}</h4>
          <small className="text-muted">
            {doc.source_type} — {new Date(doc.created_at).toLocaleDateString()}
          </small>
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
        <div key={idx} className="card mb-3">
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

      <Link to={`/assistants/${id}`} className="btn btn-outline-secondary">
        🔙 Back to Assistant
      </Link>
    </div>
  );
}
