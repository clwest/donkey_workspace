import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function AssistantLineagePage() {
  const { id } = useParams();
  const [tree, setTree] = useState(null);

  useEffect(() => {
    apiFetch(`/assistants/${id}/lineage/`)
      .then(setTree)
      .catch(() => setTree(null));
  }, [id]);

  if (!tree) return <div>Loading lineage...</div>;

  const renderNode = (node) => (
    <li key={node.id}>
      {node.name}
      {node.children && node.children.length > 0 && (
        <ul>{node.children.map((c) => renderNode(c))}</ul>
      )}
    </li>
  );

  return (
    <div className="container my-4">
      <h1 className="mb-3">Assistant Lineage</h1>
      <ul>{renderNode(tree)}</ul>
    </div>
  );
}
