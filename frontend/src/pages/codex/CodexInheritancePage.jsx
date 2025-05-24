import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import ClauseLineageViewer from "@/components/codex/ClauseLineageViewer";

export default function CodexInheritancePage() {
  const { assistantId } = useParams();
  const [data, setData] = useState([]);

  useEffect(() => {
    apiFetch(`/codex/inheritance/${assistantId}/`).then((res) => {
      setData(res.inheritance || []);
    });
  }, [assistantId]);

  return (
    <div className="container my-4">
      <h1 className="mb-3">Codex Inheritance</h1>
      <ClauseLineageViewer lineage={data} />
    </div>
  );
}
