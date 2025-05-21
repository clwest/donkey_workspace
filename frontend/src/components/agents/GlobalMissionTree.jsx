import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function GlobalMissionTree() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    apiFetch("/missions/global-tree/")
      .then(setNodes)
      .catch(() => setNodes([]));
  }, []);

  const renderNode = (node) => (
    <li key={node.id}>
      <div>
        <strong>{node.title}</strong> - <em>{node.status}</em>
        <div className="small text-muted">
          {node.assigned_assistants?.map((a) => a.name).join(", ")}
        </div>
        {node.children && node.children.length > 0 && (
          <ul>{node.children.map(renderNode)}</ul>
        )}
      </div>
    </li>
  );

  return (
    <div className="my-3">
      <h5>Global Mission Tree</h5>
      <ul className="list-unstyled">{nodes.map(renderNode)}</ul>
    </div>
  );
}

