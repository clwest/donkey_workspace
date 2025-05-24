import { useParams } from "react-router-dom";
import PromptCascadeWatcher from "../../components/swarm/PromptCascadeWatcher";

export default function PromptCascadeWatcherPage() {
  const { id } = useParams();
  return (
    <div className="container my-5">
      <h1 className="mb-3">Prompt Cascade</h1>
      <PromptCascadeWatcher promptId={id} />
    </div>
  );
}
