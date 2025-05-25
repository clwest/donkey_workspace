import { useParams } from "react-router-dom";
import BeliefForkViewer from "../../../components/agents/BeliefForkViewer"

export default function AssistantForkPage() {
  const { id } = useParams();
  return (
    <div className="container my-4">
      <h1 className="mb-3">Assistant Forks</h1>
      <BeliefForkViewer assistantId={id} />
    </div>
  );
}
