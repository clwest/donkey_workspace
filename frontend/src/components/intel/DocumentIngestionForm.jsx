import { useState, useEffect, useRef } from "react";
import apiFetch, { API_URL } from "../../utils/apiClient";
import { toast } from "react-toastify";
import DocumentIngestAggregateProgressBar from "./DocumentIngestAggregateProgressBar";

import IngestSessionLogConsole from "./IngestSessionLogConsole";
import RitualIngestStatusToast from "./RitualIngestStatusToast";


export default function DocumentIngestionForm({ onSuccess }) {
  const [urlInput, setUrlInput] = useState("");
  const [videoInput, setVideoInput] = useState("");
  const [pdfFiles, setPdfFiles] = useState([]);
  const [tags, setTags] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [log, setLog] = useState([]);
  const pollRef = useRef({});

  useEffect(() => {
    return () => {
      Object.values(pollRef.current).forEach(clearInterval);
    };
  }, []);

    const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const parsedTags = tags
      .split(",")
      .map((t) => t.trim().toLowerCase())
      .filter((t) => t.length > 0);

    const sessionId = crypto.randomUUID();
    const jobLabel = title || urlInput || videoInput || (pdfFiles[0]?.name || "Upload");

    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("session_id", sessionId);
      parsedTags.forEach((t) => formData.append("tags", t));
      if (urlInput.trim()) formData.append("urls", urlInput);
      if (videoInput.trim()) formData.append("videos", videoInput);
      pdfFiles.forEach((file) => formData.append("files", file));
      const uploadRes = await fetch(`${API_URL}/intel/document-sets/`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      if (!uploadRes.ok) throw new Error("API Error");
      await uploadRes.json();
      const newJob = {
        session_id: sessionId,
        title: jobLabel,
        stage: "parsing",
        percent_complete: 0,
        message: "",
        current_chunk: 0,
        total_chunks: 0,
      };
      setJobs((prev) => [...prev, newJob]);
      pollRef.current[sessionId] = setInterval(async () => {
        try {
          const stat = await apiFetch(`/documents/upload-status/${sessionId}/`);
          setJobs((prev) =>
            prev.map((j) =>
              j.session_id === sessionId
                ? { ...j, ...stat }
                : j
            )
          );
          setLog((l) => {
            const defaultLine = `📄 ${stat.stage} — ${jobLabel} — ${stat.percent_complete}%`;
            const chunkLine =
              stat.current_chunk && stat.total_chunks
                ? `📄 ${jobLabel} chunk ${stat.current_chunk}/${stat.total_chunks} — ${stat.percent_complete}%`
                : defaultLine;
            return [
              ...l.slice(-50),
              stat.message ? `📄 ${stat.message}` : chunkLine,
            ];
          });
          if (stat.stage === "completed") {
            clearInterval(pollRef.current[sessionId]);
            delete pollRef.current[sessionId];
            if (onSuccess) await onSuccess();
          }
        } catch (e) {
          console.error(e);
        }
      }, 3000);
      setUrlInput("");
      setVideoInput("");
      setTags("");
      setTitle("");
    } catch (err) {
      console.error("Failed to load documents:", err);
      toast.error("❌ Failed to load documents");
    } finally {
      setLoading(false);
    }
    };

  return (
    <form onSubmit={handleSubmit} className="my-4">
      <div className="mb-3">
        <label className="form-label">Title (optional)</label>
        <input
          className="form-control"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. LangChain Dev Guide"
        />
      </div>

      <div className="mb-3">
        <label className="form-label">URLs (comma-separated)</label>
        <input
          className="form-control"
          type="text"
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          placeholder="https://example.com/doc1, https://example.com/doc2"
        />
      </div>

      <div className="mb-3">
        <label className="form-label">YouTube Links (comma-separated)</label>
        <input
          className="form-control"
          type="text"
          value={videoInput}
          onChange={(e) => setVideoInput(e.target.value)}
          placeholder="https://youtu.be/example1, https://youtu.be/example2"
        />
      </div>

      <div className="mb-3">
        <label className="form-label">Upload PDFs</label>
        <input
          className="form-control"
          type="file"
          multiple
          onChange={(e) => setPdfFiles([...e.target.files])}
        />
      </div>

      <div className="mb-3">
        <label className="form-label">Tags (comma-separated)</label>
        <input
          className="form-control"
          type="text"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="ai, langchain, llm"
        />
      </div>

      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? "Uploading..." : "📥 Ingest Sources"}
      </button>


      {jobs.length > 0 && (
        <>
          <DocumentIngestAggregateProgressBar jobs={jobs} />
          <ul className="list-unstyled small mt-2">
            {jobs.map((job) => (
              <li key={job.session_id}>
                📄 {job.message || job.stage} — {job.title} — {job.percent_complete}%
              </li>
            ))}
          </ul>
          <IngestSessionLogConsole log={log} />
          <RitualIngestStatusToast progress={jobs[jobs.length - 1]} />
        </>
      )}

    </form>
  );
}
