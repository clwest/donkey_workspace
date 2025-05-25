import PrimaryStar from "../../../components/assistant/PrimaryStar";
import PropTypes from "prop-types";

export default function AssistantDashboardHeader({
  assistant,
  memoryCoverage,
  onReflect,
  onSelfAssess,
  onRegeneratePlan,
}) {
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
            {assistant.needs_recovery && (
              <span className="badge bg-warning text-dark ms-2">Misaligned</span>
            )}
            {!assistant.needs_recovery && assistant.recovered && (
              <span className="badge bg-success ms-2">Recovered</span>
            )}
          </h3>
          <p className="text-muted mb-0">{assistant.specialty}</p>
          {memoryCoverage !== null && (
            <div className="small text-muted">🧠 Memory Coverage: {memoryCoverage}%</div>
          )}
        </div>
        <div className="ms-auto d-flex gap-2">
          {onReflect && (
            <button className="btn btn-primary" onClick={onReflect}>
              Reflect Now
            </button>
          )}
          {onSelfAssess && (
            <button className="btn btn-outline-info" onClick={onSelfAssess}>
              Self-Assessment
            </button>
          )}
          {assistant.needs_recovery && onRegeneratePlan && (
            <button className="btn btn-warning" onClick={onRegeneratePlan}>
              🧠 Regenerate Plan
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

AssistantDashboardHeader.propTypes = {
  assistant: PropTypes.object,
  memoryCoverage: PropTypes.number,
  onReflect: PropTypes.func,
  onSelfAssess: PropTypes.func,
  onRegeneratePlan: PropTypes.func,
};
