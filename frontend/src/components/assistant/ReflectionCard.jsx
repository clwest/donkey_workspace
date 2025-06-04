export default function ReflectionCard({ reflection }) {
  return (
    <div className="card mb-3 p-3">
      <h5 className="mb-2">🪞 Reflection</h5>
      <div>{reflection.summary}</div>
      {reflection.tags?.length > 0 && (
        <div className="mt-2">
          <span className="text-muted small me-1">🏷 Tags:</span>
          {reflection.tags.map(tag => (
            <span key={tag.id} className="badge bg-secondary me-1">
              {tag.name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
