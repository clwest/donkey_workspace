import PropTypes from "prop-types";

const ClusterView = ({ cluster }) => {
  if (!cluster) return null;
  const { name, purpose, agents = [] } = cluster;

  return (
    <div className="cluster-view border rounded p-3 mb-3">
      <h5>{name}</h5>
      <p className="text-muted">{purpose}</p>
      <ul className="mb-0">
        {agents.map((a) => (
          <li key={a.id}>{a.name}</li>
        ))}
      </ul>
    </div>
  );
};

ClusterView.propTypes = {
  cluster: PropTypes.shape({
    name: PropTypes.string,
    purpose: PropTypes.string,
    agents: PropTypes.array,
  }),
};

export default ClusterView;
