import PropTypes from "prop-types";
import { Card, Button } from "react-bootstrap";

const TrainedAgentCard = ({ log, onPromote }) => {
  if (!log) return null;
  const { label, document_count, skill_matrix = [], created_at } = log;

  return (
    <Card className="h-100 shadow-sm">
      <Card.Body>
        <Card.Title>{label}</Card.Title>
        <Card.Subtitle className="mb-2 text-muted">
          {new Date(created_at).toLocaleString()}
        </Card.Subtitle>
        <p className="mb-1">Docs: {document_count}</p>
        <ul className="small">
          {skill_matrix.map((s) => (
            <li key={s.skill || s.name}>{s.skill || s.name} - {s.confidence ?? s.score ?? ""}</li>
          ))}
          {skill_matrix.length === 0 && <li className="text-muted">No skills</li>}
        </ul>
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
