export default function MemoryCard({ memory }) {
  return (
    <div className="card mb-2">
      <div className="card-body p-2">
        <p className="mb-1 small">{memory.preview}</p>
        <div className="text-muted small">
          {new Date(memory.created_at).toLocaleString()}
        </div>
      </div>
    </div>
  );
}
