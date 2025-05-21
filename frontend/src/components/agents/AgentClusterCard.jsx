import { Card } from "react-bootstrap";
import { Link } from "react-router-dom";

const AgentClusterCard = ({ cluster }) => {
  if (!cluster) return null;
  const { name, purpose, project, agents, skill_count, id } = cluster;
  return (
    <Card className="mb-3 shadow-sm h-100">
      <Card.Body>
        <Card.Title>{name}</Card.Title>
        <Card.Subtitle className="mb-2 text-muted">{purpose}</Card.Subtitle>
        {project && (
          <Card.Text>
            Project:{" "}
            <Link to={`/assistants/projects/${project.slug}`}>{project.title}</Link>
          </Card.Text>
        )}
        <Card.Text>
          Agents: {agents.map((a) => a.name).join(", ")} ({skill_count} skills)
        </Card.Text>
        <Link to={`/clusters/${id}`} className="btn btn-sm btn-outline-primary">
          Reflect on Cluster
        </Link>
      </Card.Body>
    </Card>
  );
};

export default AgentClusterCard;
