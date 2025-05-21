export default function MemoryCard({ memory }) {
  const summary =
    memory.summary ||
    (memory.event ? `${memory.event.slice(0, 120)}…` : "(no content)");

  return (
    <div className="card mb-2">
      <div className="card-body p-2">
        <div className="memory-summary mb-1 small">{summary}</div>
        <div className="memory-meta text-muted small">
          {new Date(memory.created_at).toLocaleString()} • {memory.token_count} tokens
        </div>
      </div>
    </div>
  );
}
