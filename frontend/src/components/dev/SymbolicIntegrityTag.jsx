export default function SymbolicIntegrityTag({ status }) {
  const colors = {
    valid: 'success',
    empty: 'secondary',
    markdown_stub: 'warning',
    error_log: 'danger',
  };
  const color = colors[status] || 'secondary';
  return (
    <span className={`badge bg-${color} ms-2`}>{status}</span>
  );
}
