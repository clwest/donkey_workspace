import { useParams } from "react-router-dom";
import useAuthGuard from "../../hooks/useAuthGuard";
import AssistantDriftPanel from "../../components/embedding/AssistantDriftPanel";

export default function AssistantDriftDiagnosticsPage() {
  useAuthGuard();
  const { slug } = useParams();
  return (
    <div className="container my-4">
      <h2 className="mb-3">Embedding Drift</h2>
      <AssistantDriftPanel slug={slug} />
    </div>
  );
}
