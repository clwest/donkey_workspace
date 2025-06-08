import { useEffect, useState } from "react";
import { Modal, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import { createAssistantFromDemo } from "@/api/assistants";

export default function DemoRecapModal({ show, onClose, demoSlug, sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!show) return;
    setLoading(true);
    apiFetch(`/assistants/demo_recap/${sessionId}/`)
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [show, sessionId]);

  const handleExport = () => {
    if (!data) return;
    const md = `# Demo Recap\n\n- Messages Sent: ${data.messages_sent}\n- Helpful Tips: ${data.tips_helpful}\n- Score: ${data.score}\n- Starter Query: ${data.starter_query}`;
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "demo_recap.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleConvert = async () => {
    setSaving(true);
    try {
      const res = await createAssistantFromDemo(demoSlug, []);
      navigate(`/assistants/${res.slug}/intro`);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Demo Recap</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading && <p>Loading recap...</p>}
        {!loading && data && (
          <div>
            <p>Messages Sent: {data.messages_sent}</p>
            <p>Helpful Tips: {data.tips_helpful}</p>
            <p>Score: {data.score}</p>
            {data.starter_query && <p>Starter: {data.starter_query}</p>}
          </div>
        )}
        {!loading && !data && <p>Failed to load recap.</p>}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleExport} disabled={loading}>
          Export Markdown
        </Button>
        <Button variant="primary" onClick={handleConvert} disabled={saving}>
          {saving ? "Converting..." : "Convert This Assistant"}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
