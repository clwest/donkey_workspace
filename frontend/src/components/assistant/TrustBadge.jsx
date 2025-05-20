export default function TrustBadge({ label }) {
  if (!label) return null;
  let className = "bg-secondary";
  let text = "Neutral";
  if (label === "trusted") {
    className = "bg-success";
    text = "Trusted Agent";
  } else if (label === "unreliable") {
    className = "bg-danger";
    text = "Unreliable";
  }
  return (
    <span className={`badge ${className} ms-2`}>
      {text}
    </span>
  );
}
