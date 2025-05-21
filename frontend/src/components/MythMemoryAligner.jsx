export default function MythMemoryAligner({ conflicts = [] }) {
  if (conflicts.length === 0) return <div>No conflicts detected.</div>;

  return (
    <div className="p-3 border rounded bg-light">
      <h5>Myth Memory Aligner</h5>
      {conflicts.map((c, i) => (
        <div key={i} className="mb-2">
          <strong>{c.source}</strong>
          <p className="mb-1 small">{c.content}</p>
        </div>
      ))}
      <button className="btn btn-sm btn-outline-primary">Suggest Alignment</button>
    </div>
  );
}
