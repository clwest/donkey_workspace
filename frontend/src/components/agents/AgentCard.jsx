import { Card } from "react-bootstrap";
import { Link } from "react-router-dom";
import TrustBadge from "../assistant/TrustBadge";

const AgentCard = ({ agent }) => {
  if (!agent) return null;

  const {
    name = "Unnamed Agent",
    slug = "#",
    preferred_llm = "Unknown LLM",
    execution_mode = "default",
    avatar_url = null,
    trust = null,
  } = agent;

  return (
    <Card className="mb-3 shadow-sm h-100">
      <Card.Body>
        <Card.Title>
          <Link to={`/agents/${slug}`} className="text-decoration-none">
            {name}
          </Link>
          <TrustBadge label={trust?.overall_label} />
        </Card.Title>
        <Card.Subtitle className="mb-2 text-muted">LLM: {preferred_llm}</Card.Subtitle>
        <Card.Text>
          <strong>Execution Mode:</strong> {execution_mode}
        </Card.Text>
      </Card.Body>
    </Card>
  );
};

export default AgentCard;