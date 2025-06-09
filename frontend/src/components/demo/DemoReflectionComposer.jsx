import { useEffect, useState } from "react";
import CommonModal from "../CommonModal";
import { composeDemoReflection } from "@/api/assistants";
import DriftDiagnosisPanel from "./DriftDiagnosisPanel";

export default function DemoReflectionComposer({ slug, sessionId, show, onClose }) {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!show) return;
    setLoading(true);
    composeDemoReflection(slug, sessionId)
      .then((d) => {
        setSummary(d.summary || "");
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [show, slug, sessionId]);

  const handleSave = async () => {
    await composeDemoReflection(slug, sessionId, true);
    onClose();
  };

  return (
    <>
      <CommonModal
        show={show}
        onClose={onClose}
        title="📘 Demo Reflection"
        footer={
          <>
            <button className="btn btn-secondary" onClick={onClose}>
              Dismiss
            </button>
            <button className="btn btn-primary" onClick={handleSave}>
              Accept
            </button>
          </>
        }
      >
        {loading ? (
          <p>Composing...</p>
        ) : (
          <textarea
            className="form-control"
            rows={6}
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
          />
        )}
      </CommonModal>
      <DriftDiagnosisPanel slug={slug} sessionId={sessionId} />
    </>
  );
}
