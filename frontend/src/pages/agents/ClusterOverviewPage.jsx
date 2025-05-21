import { useEffect, useState } from "react";
import AgentClusterCard from "../../components/agents/AgentClusterCard";
import apiFetch from "../../utils/apiClient";

const ClusterOverviewPage = () => {
  const [clusters, setClusters] = useState([]);

  useEffect(() => {
    apiFetch("/agents/clusters/")
      .then(setClusters)
      .catch((err) => console.error("Failed to load clusters", err));
  }, []);

  return (
    <div className="container py-4">
      <h1 className="mb-4">Agent Clusters</h1>
      <div className="row">
        {clusters.map((cluster) => (
          <div key={cluster.id} className="col-md-4 mb-3">
            <AgentClusterCard cluster={cluster} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ClusterOverviewPage;
