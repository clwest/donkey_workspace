import { useParams } from "react-router-dom";
import AssistantRunTaskPanel from "@/components/assistant/AssistantRunTaskPanel";

export default function RunTaskPage() {
  const { id } = useParams();
  return (
    <div className="container my-4">
      <h1 className="mb-3">Run Task</h1>
      <AssistantRunTaskPanel slug={id} />
    </div>
  );
}
