import Modal from "../CommonModal";

export default function SelfAssessmentModal({ show, onClose, result, onApply }) {
  if (!result) return null;
  const score = result.score || 0;
  const badge = score >= 0.8 ? "success" : score >= 0.5 ? "warning" : "danger";
  const footer = (
    <div className="d-flex justify-content-end w-100">
      {onApply && (
        <button className="btn btn-primary me-2" onClick={onApply}>
          Apply Changes
        </button>
      )}
      <button className="btn btn-secondary" onClick={onClose}>
        Close
      </button>
    </div>
  );
  return (
    <Modal show={show} onClose={onClose} title="Self Assessment" footer={footer}>
      <div className="mb-2">
        <span className={`badge bg-${badge}`}>{score.toFixed(2)}</span>
      </div>
      {result.role && (
        <p>
          <strong>Role:</strong> {result.role}
        </p>
      )}
      {result.summary && <p>{result.summary}</p>}
      {result.prompt_tweaks && (
        <pre className="small bg-light p-2">{result.prompt_tweaks}</pre>
      )}
    </Modal>
  );
}
