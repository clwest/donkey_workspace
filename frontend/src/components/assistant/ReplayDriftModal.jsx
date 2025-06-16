export default function ReplayDriftModal({ snapshots, onClose }) {
  return (
    <div className="modal d-block" tabIndex="-1" role="dialog">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Replay Diff</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body" style={{ maxHeight: "70vh", overflowY: "auto" }}>
            {snapshots.map((s) => (
              <div key={s.id} className="mb-4">
                <h6>{new Date(s.created_at).toLocaleString()}</h6>
                <pre className="border p-2" style={{ whiteSpace: "pre-wrap" }}>{s.diff_text}</pre>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
