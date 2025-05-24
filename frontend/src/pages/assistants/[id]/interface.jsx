import { useParams } from "react-router-dom";
import CodexAnchorPanel from "@/components/assistant/CodexAnchorPanel";
import RitualLaunchpadPanel from "@/components/assistant/RitualLaunchpadPanel";
import BeliefForkViewer from "@/components/assistant/BeliefForkViewer";
import AssistantThoughtStream from "@/components/assistant/AssistantThoughtStream";

export default function AssistantInterface() {
  const { id } = useParams();
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-6">
      <div className="space-y-4">
        <CodexAnchorPanel assistantId={id} />
        <RitualLaunchpadPanel assistantId={id} />
      </div>
      <div className="space-y-4">
        <BeliefForkViewer assistantId={id} />
        <AssistantThoughtStream assistantId={id} />
      </div>
    </div>
  );
}
