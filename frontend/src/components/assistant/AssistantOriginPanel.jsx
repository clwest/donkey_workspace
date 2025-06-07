import { Link } from "react-router-dom";

export default function AssistantOriginPanel({ assistant }) {
  if (!assistant?.is_cloned_from_demo) return null;
  const traits = assistant.spawned_traits || [];
  const icons = {
    badge: "🏅 Badge",
    tone: "🧠 Tone",
    avatar: "🎭 Avatar",
  };
  const inherited = traits.map((t) => icons[t] || t).join(", ");
  return (
    <div className="alert alert-info mt-3">
      <p className="mb-1">
        Your assistant was created from 🧪 <strong>{assistant.spawned_by_label}</strong>, a demo built to help you explore prompts.
      </p>
      {inherited && (
        <p className="mb-2">You inherited: {inherited}</p>
      )}
      <Link to={`/assistants/${assistant.slug}/edit`} className="btn btn-sm btn-primary">
        Customize Further
      </Link>
    </div>
  );
}
