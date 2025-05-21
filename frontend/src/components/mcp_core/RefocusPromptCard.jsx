export default function RefocusPromptCard({ prompt }) {
  if (!prompt) return null;
  return (
    <div className="alert alert-warning">
      <strong>🩹 Refocus Suggestion</strong>
      <p className="mb-0" style={{ whiteSpace: "pre-line" }}>
        {prompt}
      </p>
    </div>
  );
}
