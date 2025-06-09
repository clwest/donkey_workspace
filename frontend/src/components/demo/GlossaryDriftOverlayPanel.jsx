import { useEffect, useState } from "react";
import { Modal } from "react-bootstrap";
import apiFetch from "@/utils/apiClient";
import DriftDiagnosisPanel from "./DriftDiagnosisPanel";

export default function GlossaryDriftOverlayPanel({ slug, sessionId }) {
  const [logs, setLogs] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    if (!slug || !sessionId) return;
    apiFetch(`/assistants/${slug}/demo_session/${sessionId}/rag_overlay/`)
      .then(setLogs)
      .catch(() => {});
  }, [slug, sessionId]);

  if (!logs.length) return null;

  return (
    <div className="demo-overlay border rounded p-3 mt-3">
      <h5 className="mb-2">Drift Overlay</h5>
      <div className="d-flex flex-wrap gap-2 mb-2">
        {logs.map((l, i) => (
          <span
            key={l.id}
            role="button"
            className="badge bg-secondary"
            onClick={() => setSelected(l)}
          >
            {i + 1} {l.chunks.some((c) => c.is_fallback) ? "⚠️" : l.chunks.some((c) => c.anchor_match) ? "🧠" : "✅"}
          </span>
        ))}
      </div>
      <Modal show={!!selected} onHide={() => setSelected(null)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Chunk Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selected &&
            selected.chunks.map((c) => (
              <div key={c.id} className="mb-2">
                <div className="small text-muted">{c.id}</div>
                <div>Score: {c.glossary_score?.toFixed?.(2)}</div>
                <div>{c.text}</div>
              </div>
            ))}
        </Modal.Body>
      </Modal>
      <DriftDiagnosisPanel slug={slug} sessionId={sessionId} />
    </div>
  );
}
