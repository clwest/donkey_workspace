import {useEffect, useState} from "react";
import {Modal} from "react-bootstrap";
import PropTypes from "prop-types";
import apiFetch from "@/utils/apiClient";

export default function AssistantRefinementWizard({ slug, sessionId, show, onClose }) {
  const [step, setStep] = useState(1);
  const [data, setData] = useState(null);
  const total = 5;

  useEffect(() => {
    if (!show) return;
    apiFetch(`/assistants/${slug}/refine_from_drift/`, {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    })
      .then(setData)
      .catch(() => {});
  }, [show, slug, sessionId]);

  if (!show) return null;

  const next = () => setStep((s) => Math.min(total, s + 1));
  const back = () => setStep((s) => Math.max(1, s - 1));

  return (
    <Modal show={show} onHide={onClose} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>Assistant Refinement</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {step === 1 && data && (
          <div>
            <h5>Drift Summary</h5>
            {data.drift && data.drift.diagnosis && (
              <div className="mb-2">
                {data.drift.diagnosis.map((d) => (
                  <span key={d} className="badge bg-warning text-dark me-1">
                    {d}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
        {step === 2 && data && (
          <div>
            <h5>Glossary Fix Suggestions</h5>
            {data.glossary_fixes && data.glossary_fixes.length ? (
              <ul>
                {data.glossary_fixes.map((g) => (
                  <li key={g.term}>
                    {g.term} <span className="text-muted">({g.cause})</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No glossary suggestions.</p>
            )}
          </div>
        )}
        {step === 3 && data && (
          <div>
            <h5>Prompt Revision Draft</h5>
            {data.prompt_revision ? (
              <>
                <pre className="bg-light p-2 mb-2">{data.prompt_revision.before}</pre>
                <pre className="bg-light p-2">{data.prompt_revision.after}</pre>
              </>
            ) : (
              <p>No prompt changes suggested.</p>
            )}
          </div>
        )}
        {step === 4 && data && (
          <div>
            <h5>New Tone/Badge Suggestions</h5>
            {data.tone_tags && data.tone_tags.length ? (
              <div className="d-flex flex-wrap gap-1">
                {data.tone_tags.map((t) => (
                  <span key={t} className="badge bg-secondary">
                    {t}
                  </span>
                ))}
              </div>
            ) : (
              <p>No tone mismatches detected.</p>
            )}
          </div>
        )}
        {step === 5 && <p>Confirm the refinements and continue.</p>}
      </Modal.Body>
      <Modal.Footer>
        {step > 1 && (
          <button className="btn btn-secondary me-2" onClick={back}>
            Back
          </button>
        )}
        {step < total && (
          <button className="btn btn-primary" onClick={next}>
            Next
          </button>
        )}
        {step === total && (
          <button className="btn btn-success" onClick={onClose}>
            Save
          </button>
        )}
      </Modal.Footer>
    </Modal>
  );
}

AssistantRefinementWizard.propTypes = {
  slug: PropTypes.string.isRequired,
  sessionId: PropTypes.string,
  show: PropTypes.bool,
  onClose: PropTypes.func,
};
