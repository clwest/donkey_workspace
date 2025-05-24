export default function EntropyTagPanel({ tags }) {
  if (!tags || tags.length === 0) return null;
  return (
    <div className="mt-3">
      <h5>Entropy Tags</h5>
      <ul className="list-inline mb-0">
        {tags.map((tag, idx) => (
          <li key={idx} className="list-inline-item badge bg-warning text-dark">
            {tag}
          </li>
        ))}
      </ul>
    </div>
  );
}
