import { useEffect, useState } from "react";
import { fetchDeploymentReadiness, triggerDeployment } from "../../api/assistants";

export default function DeploymentPlanner({ assistantId }) {
  const [readiness, setReadiness] = useState(null);
  const [label, setLabel] = useState("");

  useEffect(() => {
    if (!assistantId) return;
    fetchDeploymentReadiness(assistantId)
      .then(setReadiness)
      .catch(() => setReadiness(null));
  }, [assistantId]);

  const handleDeploy = async () => {
    try {
      await triggerDeployment(assistantId, { label });
      alert("Deployment queued");
    } catch (e) {
      console.error(e);
    }
  };

  if (!readiness) return <div>Loading deployment info...</div>;

  return (
    <div className="my-3">
      <h5>Deployment Planner</h5>
      <pre className="bg-light p-2 rounded">
        {JSON.stringify(readiness.readiness, null, 2)}
      </pre>
      <div className="mt-2">
        <input
          type="text"
          className="form-control mb-2"
          placeholder="Label"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
        />
        <button className="btn btn-primary" onClick={handleDeploy}>
          Deploy
        </button>
      </div>
    </div>
  );
}
