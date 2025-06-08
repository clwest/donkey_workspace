import { Link } from "react-router-dom";

export default function DemoAssistantShowcase({ assistants = [] }) {
  if (!assistants.length) return null;
  return (
    <div className="mb-4">
      <h2 className="h5 mb-3">Featured Assistants</h2>
      <div className="d-flex flex-wrap gap-3">
        {assistants.map((a) => (
          <div
            key={a.id}
            className="card shadow-sm border-0 position-relative"
            style={{ width: "18rem" }}
          >
            <span className="badge bg-warning position-absolute top-0 start-0">
              🏆 Featured
            </span>
            <div className="card-body">
              <h5 className="card-title mb-1">{a.name}</h5>
              <p className="small text-muted">
                {a.intro_text || a.description || "Try this assistant"}
              </p>
              <Link
                to={`/assistants/${a.demo_slug || a.slug}/chat`}
                className="btn btn-success btn-sm"
              >
                Try Now
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
