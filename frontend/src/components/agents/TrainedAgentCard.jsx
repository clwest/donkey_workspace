import PropTypes from "prop-types";
import { useState } from "react";
import { Card, Button } from "react-bootstrap";

const TrainedAgentCard = ({ log, onPromote }) => {
  if (!log) return null;
  const {
    label,
    prompt,
    document_set,
    document_count,
    skill_matrix = [],
    created_at,
  } = log;
  const [showSkills, setShowSkills] = useState(false);

  return (
    <Card className="h-100 shadow-sm">
      <Card.Body>
        <Card.Title>{label}</Card.Title>
        <Card.Subtitle className="mb-2 text-muted">
          {new Date(created_at).toLocaleString()}
        </Card.Subtitle>
        {prompt && (
          <p className="mb-1">
            <strong>Prompt:</strong> {prompt.title}
          </p>
        )}
        {document_set && (
          <p className="mb-1">
            <strong>Document Set:</strong> {document_set.title}
          </p>
        )}
        <p className="mb-1">Docs: {document_count}</p>
        {skill_matrix.length > 0 && (
          <>
            <Button
              variant="outline-secondary"
              size="sm"
              className="mb-2"
              onClick={() => setShowSkills(!showSkills)}
            >
              {showSkills ? "Hide Skills" : "Show Skills"}
            </Button>
            {showSkills && (
              <div className="d-flex flex-wrap mb-2">
                {skill_matrix.map((s) => (
                  <span
                    key={s.skill || s.name}
                    className="badge bg-secondary me-1 mb-1"
                  >
                    {s.skill || s.name}
                    {s.confidence != null || s.score != null ? (
                      <span className="ms-1">
                        ({Math.round(((s.confidence ?? s.score) || 0) * 100)}%)
                      </span>
                    ) : null}
                  </span>
                ))}
              </div>
            )}
          </>
        )}
        {skill_matrix.length === 0 && (
          <p className="text-muted">No skills</p>
        )}
        {onPromote && (
          <Button variant="primary" size="sm" onClick={onPromote}>
            Promote to Assistant
          </Button>
        )}
      </Card.Body>
    </Card>
  );
};

TrainedAgentCard.propTypes = {
  log: PropTypes.object,
  onPromote: PropTypes.func,
};

export default TrainedAgentCard;
