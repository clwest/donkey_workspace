export default function ThoughtCard({ thought }) {
  return (
    <div className="card mb-2 bg-light">
      <div className="card-body p-2">
        <p className="mb-1 small">{thought.content}</p>
        <div className="text-muted small">
          {thought.type} • {thought.model}
        </div>
      </div>
    </div>
  );
}
