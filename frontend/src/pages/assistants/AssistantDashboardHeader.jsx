import PrimaryStar from "../../components/assistant/PrimaryStar";

export default function AssistantDashboardHeader({ assistant, memoryCoverage, onReflect }) {
  if (!assistant) return null;
  return (
    <div className="card mb-4 shadow-sm">
      <div className="card-body d-flex align-items-center">
        {assistant.avatar && (
          <img
            src={assistant.avatar}
            alt="avatar"
            className="rounded-circle me-3"
            width="60"
            height="60"
          />
        )}
        <div>
          <h3 className="mb-0">
            {assistant.name} <PrimaryStar isPrimary={assistant.is_primary} />
          </h3>
          <p className="text-muted mb-0">{assistant.specialty}</p>
          {memoryCoverage !== null && (
            <div className="small text-muted">🧠 Memory Coverage: {memoryCoverage}%</div>
          )}
        </div>
        {onReflect && (
          <div className="ms-auto">
            <button className="btn btn-primary" onClick={onReflect}>
              Reflect Now
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
