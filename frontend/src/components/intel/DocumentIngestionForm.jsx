import { useState, useEffect } from "react";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import DocumentIngestingCard from "../documents/DocumentIngestingCard";
import useUserInfo from "@/hooks/useUserInfo";

export default function DocumentIngestionForm({ onSuccess }) {
  const [urlInput, setUrlInput] = useState("");
  const [videoInput, setVideoInput] = useState("");
  const [pdfFiles, setPdfFiles] = useState([]);
  const [tags, setTags] = useState("");
  const [title, setTitle] = useState("");
  const [assistants, setAssistants] = useState([]);
  const [selectedSlug, setSelectedSlug] = useState("");
  const [loading, setLoading] = useState(false);
  const [reflectAfter, setReflectAfter] = useState(false);
  const [pendingDocs, setPendingDocs] = useState([]);
  const navigate = useNavigate();
  const userInfo = useUserInfo();

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

  useEffect(() => {
    if (userInfo?.primary_assistant_slug) {
      setSelectedSlug(userInfo.primary_assistant_slug);
    }
  }, [userInfo]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const parsedTags = tags
      .split(",")
      .map((t) => t.trim().toLowerCase())
      .filter((t) => t.length > 0);
    const urlList = urlInput
      .split(",")
      .map((u) => u.trim())
      .filter((u) => u.length > 0);
    const videoList = videoInput
      .split(",")
      .map((u) => u.trim())
      .filter((u) => u.length > 0);

    try {
      let sourceType = "";
      if (pdfFiles.length > 0) {
        sourceType = "pdf";
      } else if (videoInput.trim()) {
        sourceType = "youtube";
      } else if (urlInput.trim()) {
        sourceType = "url";
      }

      if (!sourceType) {
        toast.error("Please provide a URL, video, or PDF to ingest");
        setLoading(false);
        return;
      }
      const selectedAssistant = assistants.find((a) => a.slug === selectedSlug);
      console.log("Ingesting for assistant:", selectedAssistant?.id);

      const formData = new FormData();
      formData.append("title", title);
      if (selectedAssistant?.id)
        formData.append("assistant_id", selectedAssistant.id);
      formData.append("reflect_after", reflectAfter ? "true" : "false");
      formData.append("source_type", sourceType);
      if (parsedTags.length > 0) {
        formData.append("tags", JSON.stringify(parsedTags));
      }
      const combinedUrls = sourceType === "youtube" ? videoList : urlList;
      if (combinedUrls.length > 0) {
        formData.append("urls", JSON.stringify(combinedUrls));
      }
      pdfFiles.forEach((file) => formData.append("files", file));
      const data = await apiFetch(`/intel/ingest/`, {
        method: "POST",
        body: formData,
      });
      if (!data) {
        toast.error("Ingestion failed: invalid response");
        setLoading(false);
        return;
      }

      if (Array.isArray(data.documents)) {
        for (const doc of data.documents) {
          const docId = doc.document_id || doc.id;
          if (!docId) continue;
          try {
            const full = await apiFetch(`/intel/documents/${docId}/`);
            setPendingDocs((prev) => [...prev, full]);
          } catch (err) {
            console.error("Failed to fetch doc", err);
          }
        }
      }

      if (onSuccess) await onSuccess();
      if (
        reflectAfter &&
        selectedAssistant?.id &&
        data &&
        data.documents?.length > 0
      ) {
        const firstDoc = data.documents[0];
        const docId = firstDoc.document_id || firstDoc.id;
        if (!docId || docId === "undefined") {
          console.warn(
            `[ReviewIngest] Skipping review — invalid document ID: ${docId}`,
          );
        } else {
          navigate(
            `/assistants/${selectedAssistant.slug}/review-ingest/${docId}/`,
          );
          return;
        }
      }
      if (
        (data && data.status === "skipped") ||
        (data &&
          Array.isArray(data.documents) &&
          data.documents.some(
            (d) => d.status === "skipped" || d.total_chunks === 0,
          ))
      ) {
        toast.warn(data.reason || "Ingestion skipped");
      } else {
        toast.success("Ingestion complete");
      }
      setUrlInput("");
      setVideoInput("");
      setTags("");
      setTitle("");
      setPdfFiles([]);
      setSelectedSlug("");
      setReflectAfter(false);
    } catch (err) {
      console.error("Failed to load documents:", err);
      toast.error("❌ Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
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

        {!userInfo?.primary_assistant_slug && (
          <div className="mb-3">
            <label className="form-label">Assign to Assistant</label>
            <select
              className="form-select"
              value={selectedSlug}
              onChange={(e) => setSelectedSlug(e.target.value)}
            >
              <option value="">-- Select an assistant --</option>
              {assistants.map((a) => (
                <option key={a.id} value={a.slug}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
        )}

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

      {pendingDocs.length > 0 && (
        <div className="row mt-4">
          {pendingDocs.map((doc) => (
            <div key={doc.id} className="col-md-6 col-lg-4 mb-4">
              <DocumentIngestingCard doc={doc} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
