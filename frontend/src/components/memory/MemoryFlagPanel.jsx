export default function MemoryFlagPanel({ flags }) {
  if (!flags || flags.length === 0) return null;

  return (
    <div className="alert alert-warning mt-3">
      <strong>⚠️ ReflectionGuard triggered {flags.length} time(s)</strong>
      <ul className="mb-0 mt-2">
        {flags.map((flag, index) => (
          <li key={index}>
            <span className="fw-semibold">{flag.severity.toUpperCase()}:</span> {flag.reason}
          </li>
        ))}
      </ul>
    </div>
  );
}