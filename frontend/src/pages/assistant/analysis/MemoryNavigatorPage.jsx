import { useParams } from "react-router-dom";
import MemoryNavigatorTimeline from "../../../components/assistant/analysis/MemoryNavigatorTimeline";

export default function MemoryNavigatorPage() {
  const { slug } = useParams();
  return (
    <div className="container my-5">
      <h2 className="mb-4">Memory Timeline for {slug}</h2>
      <MemoryNavigatorTimeline assistantId={slug} />
    </div>
  );
}
