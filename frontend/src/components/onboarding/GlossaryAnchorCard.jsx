export default function GlossaryAnchorCard({ anchor, onTeach }) {
  return (
    <div className="card p-3" style={{ width: "16rem" }}>
      <h5 className="mb-1">{anchor.label}</h5>
      <p className="mb-1 small text-muted">{anchor.description}</p>
      {anchor.location && (
        <small className="text-muted">{anchor.location}</small>
      )}
      <button
        className="btn btn-sm btn-primary mt-2"
        onClick={() => onTeach(anchor)}
      >
        Teach This
      </button>
    </div>
  );
}
