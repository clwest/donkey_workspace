import { useState, useEffect, useRef } from "react";
import apiFetch, { API_URL } from "../../utils/apiClient";
import { toast } from "react-toastify";
import DocumentUploadProgressBar from "./DocumentUploadProgressBar";

import SymbolicChunkLogViewer from "./SymbolicChunkLogViewer";
import RitualIngestStatusToast from "./RitualIngestStatusToast";


export default function DocumentIngestionForm({ onSuccess }) {
  const [urlInput, setUrlInput] = useState("");
  const [videoInput, setVideoInput] = useState("");
  const [pdfFiles, setPdfFiles] = useState([]);
  const [tags, setTags] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null);
  const [log, setLog] = useState([]);
  const pollRef = useRef(null);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
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
      setProgress({ stage: "parsing", percent_complete: 0 });
      pollRef.current = setInterval(async () => {
        try {
          const stat = await apiFetch(
            `/documents/upload-status/${sessionId}/`
          );
          setProgress(stat);
          setLog((l) => [...l.slice(-10), `${stat.stage} ${stat.percent_complete}%`]);
          if (stat.stage === "completed") {
            clearInterval(pollRef.current);
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


      {progress && (
        <>
          <DocumentUploadProgressBar progress={progress} />
          <SymbolicChunkLogViewer log={log} />
          <RitualIngestStatusToast progress={progress} />
        </>
      )}

    </form>
  );
}
