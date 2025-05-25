import { useParams } from "react-router-dom";
import AssistantThoughtStream from "@/components/assistant/AssistantThoughtStream";

export default function ThoughtLogPanel() {
  const { id } = useParams();
  return (
    <div className="container my-4">
      <h3>Thought Log</h3>
      <AssistantThoughtStream assistantId={id} />
    </div>
  );
}
