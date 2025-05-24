export default function IdentityGlyphPreview({ vector = {} }) {
  const text = JSON.stringify(vector).slice(0, 12);
  return (
    <div className="border rounded p-3 text-center">
      <div className="fw-bold">Identity Glyph</div>
      <div style={{ fontFamily: 'monospace' }}>{text}</div>
    </div>
  );
}
