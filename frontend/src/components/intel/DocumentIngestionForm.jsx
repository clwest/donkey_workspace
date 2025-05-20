import { useState, useEffect, useRef } from "react";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function DocumentIngestionForm({ onSuccess }) {
  const [urlInput, setUrlInput] = useState("");
  const [videoInput, setVideoInput] = useState("");
  const [pdfFiles, setPdfFiles] = useState([]);
  const [tags, setTags] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null);
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

    const payload = {
        title,
        project_name: "General",
        session_id: "00000000-0000-0000-0000-000000000000",
        tags: parsedTags,
    };

    try {
        let res;
        if (pdfFiles.length > 0) {
        const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
        const formData = new FormData();
        formData.append("source_type", "pdf");
        formData.append("title", title);
        formData.append("project_name", "General");
        formData.append("session_id", "00000000-0000-0000-0000-000000000000");
        parsedTags.forEach((t) => formData.append("tags", t));
        pdfFiles.forEach((file) => formData.append("files", file));
        console.log("Uploading PDFs", pdfFiles);
        const uploadRes = await fetch(`${API_URL}/intel/ingestions/`, {
            method: "POST",
            body: formData,
            credentials: "include",
        });
        if (!uploadRes.ok) throw new Error("API Error");
        res = await uploadRes.json();
        const first = res.documents && res.documents[0];
        const progressId = first?.metadata?.progress_id;
        if (progressId) {
          pollRef.current = setInterval(async () => {
            try {
              const data = await apiFetch(`/intel/documents/${progressId}/progress/`);
              setProgress(data);
              if (data.status !== "in_progress" && pollRef.current) {
                clearInterval(pollRef.current);
                pollRef.current = null;
              }
            } catch (err) {
              console.error("Progress polling failed", err);
              clearInterval(pollRef.current);
              pollRef.current = null;
            }
          }, 2000);
        }
        } else if (urlInput.trim()) {
        payload.urls = urlInput
            .split(",")
            .map((u) => u.trim())
            .filter((u) => u.length > 0);
        payload.source_type = "url";
        res = await apiFetch("/intel/ingestions/", {
            method: "POST",
            body: payload,
        });
        } else if (videoInput.trim()) {
        payload.urls = videoInput
            .split(",")
            .map((u) => u.trim())
            .filter((u) => u.length > 0);
        payload.source_type = "youtube";
        res = await apiFetch("/intel/ingestions/", {
            method: "POST",
            body: payload,
        });
        } else {
        throw new Error("No input provided for URL, YouTube, or PDF");
        }

        toast.success(`✅ Loaded ${res.documents?.length || 0} documents!`);
        if (onSuccess) await onSuccess();
        // Log the API response for debugging purposes
        console.log(res);
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
        <div className="mt-3">
          <div className="progress">
            <div
              className="progress-bar"
              role="progressbar"
              style={{ width: `${(progress.processed / progress.total_chunks) * 100}%` }}
              aria-valuenow={progress.processed}
              aria-valuemin="0"
              aria-valuemax={progress.total_chunks}
            ></div>
          </div>
          <small className="text-muted">
            {progress.status === "completed"
              ? `✅ ${progress.processed}/${progress.total_chunks} complete`
              : `📄 Processing chunk ${progress.processed}/${progress.total_chunks}...`}
          </small>
        </div>
      )}
    </form>
  );
}
