import { useState, useEffect } from "react";
import apiFetch, { API_URL } from "../../utils/apiClient";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

export default function DocumentIngestionForm({ onSuccess }) {
  const [urlInput, setUrlInput] = useState("");
  const [videoInput, setVideoInput] = useState("");
  const [pdfFiles, setPdfFiles] = useState([]);
  const [tags, setTags] = useState("");
  const [title, setTitle] = useState("");
  const [assistants, setAssistants] = useState([]);
  const [selectedAssistant, setSelectedAssistant] = useState("");
  const [loading, setLoading] = useState(false);
  const [reflectAfter, setReflectAfter] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchAssistants() {
      try {
        const res = await apiFetch("/assistants/?limit=100");
        setAssistants(res.results || res);
      } catch (err) {
        console.error("Failed to load assistants", err);
      }
    }
    fetchAssistants();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const parsedTags = tags
      .split(",")
      .map((t) => t.trim().toLowerCase())
      .filter((t) => t.length > 0);

    try {
      const formData = new FormData();
      formData.append("title", title);
      if (selectedAssistant) formData.append("assistant_id", selectedAssistant);
      formData.append("reflect_after", reflectAfter ? "true" : "false");
      parsedTags.forEach((t) => formData.append("tags", t));
      if (urlInput.trim()) formData.append("urls", urlInput);
      if (videoInput.trim()) formData.append("videos", videoInput);
      pdfFiles.forEach((file) => formData.append("files", file));
      const uploadRes = await fetch(`${API_URL}/intel/ingest/`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      if (!uploadRes.ok) throw new Error("API Error");
      const data = await uploadRes.json();
      if (onSuccess) await onSuccess();
      if (reflectAfter && selectedAssistant && data.documents?.length > 0) {
        const asst = assistants.find((a) => a.id === selectedAssistant);
        if (asst) {
          navigate(
            `/assistants/${asst.slug}/review-ingest/${data.documents[0].id}/`,
          );
          return;
        }
      }
      toast.success("Ingestion complete");
      setUrlInput("");
      setVideoInput("");
      setTags("");
      setTitle("");
      setPdfFiles([]);
      setSelectedAssistant("");
      setReflectAfter(false);
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
        <label className="form-label">Assign to Assistant</label>
        <select
          className="form-select"
          value={selectedAssistant}
          onChange={(e) => setSelectedAssistant(e.target.value)}
        >
          <option value="">-- Select an assistant --</option>
          {assistants.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
      </div>

      <div className="form-check mb-3">
        <input
          className="form-check-input"
          type="checkbox"
          id="reflectAfter"
          checked={reflectAfter}
          onChange={(e) => setReflectAfter(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="reflectAfter">
          Reflect after ingest
        </label>
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
