import { useEffect, useState } from "react";
import { Modal, Button } from "react-bootstrap";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import apiFetch from "@/utils/apiClient";
import { createAssistantFromDemo } from "@/api/assistants";
import DemoOverlayPanel from "./DemoOverlayPanel";
import DriftDiagnosisPanel from "./DriftDiagnosisPanel";

const suggestions = [
  "Reflect on birth",
  "Create a first objective",
  "Start a memory chain",
];

export default function DemoRecapModal({ show, onClose, demoSlug, sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showNurture, setShowNurture] = useState(
    localStorage.getItem("demoNurtureDismissed") !== "true"
  );
  const [showOverlay, setShowOverlay] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    if (!show) return;
    setLoading(true);
    apiFetch(`/assistants/demo_recap/${sessionId}/`)
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((err) => {
        if (err.status === 404 || err.status === 403) {
          console.warn('Demo recap not available');
        } else {
          console.error('Failed to load recap', err);
        }
        setLoading(false);
      });
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

  const dismissNurture = () => {
    localStorage.setItem("demoNurtureDismissed", "true");
    setShowNurture(false);
  };

  return (
    <>
    <Modal show={show} onHide={onClose} centered aria-labelledby="demoRecapTitle">
      <Modal.Header closeButton>
        <Modal.Title id="demoRecapTitle">{t('demorecap.title')}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading && (
          <div className="my-3 text-center">
            <div className="spinner-border" role="status" />
          </div>
        )}
        {!loading && data && (
          <div>
            <p>{t('demorecap.messages')}: {data.messages_sent}</p>
            <p>{t('demorecap.tips')}: {data.tips_helpful}</p>
            <p>{t('demorecap.score')}: {data.score}</p>
            {data.starter_query && <p>{t('demorecap.starter')}: {data.starter_query}</p>}
            {showNurture && (
              <div className="mt-3 border-top pt-2">
                <p className="mb-1">Next steps to nurture your clone:</p>
                <ul className="mb-2">
                  {suggestions.map((s) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
                <button className="btn btn-sm btn-outline-secondary" onClick={dismissNurture}>
                  Dismiss
                </button>
              </div>
            )}
          </div>
        )}
        {!loading && !data && <p>No recap available.</p>}
      </Modal.Body>
      <Modal.Footer className="flex-wrap gap-2">
        <Button variant="secondary" onClick={handleExport} disabled={loading}>
          Export Markdown
        </Button>
        <Button variant="info" onClick={() => setShowOverlay((v) => !v)}>
          {showOverlay ? t('demorecap.view_overlay') : t('demorecap.view_overlay')}
        </Button>
        <Button variant="primary" onClick={handleConvert} disabled={saving}>
          {saving ? "Converting..." : "Convert This Assistant"}
        </Button>
        <Button variant="outline-secondary" onClick={onClose}>
          Continue with this Assistant
        </Button>
        <a className="btn btn-link" href="/assistants/create">
          Create Another
        </a>
        <Link to="/assistants/demos/success" className="btn btn-link">
          Explore Other Successes
        </Link>
      </Modal.Footer>
    </Modal>
    {showOverlay && (
      <div className="mt-3">
        <DemoOverlayPanel slug={demoSlug} sessionId={sessionId} />
        <DriftDiagnosisPanel slug={demoSlug} sessionId={sessionId} />
      </div>
    )}
    </>
  );
}
