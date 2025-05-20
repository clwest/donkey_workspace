import { useState } from "react";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function DocumentIngestionForm({ onSuccess }) {
  const [urlInput, setUrlInput] = useState("");
  const [videoInput, setVideoInput] = useState("");
  const [pdfFiles, setPdfFiles] = useState([]);
  const [tags, setTags] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
        title,
        project_name: "General",
        session_id: "00000000-0000-0000-0000-000000000000",
        tags: tags
        .split(",")
        .map((t) => t.trim().toLowerCase())
        .filter((t) => t.length > 0),
    };

    try {
        if (urlInput.trim()) {
        payload.urls = urlInput
            .split(",")
            .map((u) => u.trim())
            .filter((u) => u.length > 0);
        payload.source_type = "url";
        } else if (videoInput.trim()) {
        payload.urls = videoInput
            .split(",")
            .map((u) => u.trim())
            .filter((u) => u.length > 0);
        payload.source_type = "youtube";
        } else {
        throw new Error("No input provided for URL or YouTube");
        }

        const res = await apiFetch("/intel/ingestions/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        });

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
    </form>
  );
}
