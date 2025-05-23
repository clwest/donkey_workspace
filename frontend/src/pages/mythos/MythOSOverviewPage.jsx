import VisualArchetypeCard from "../../components/swarm/VisualArchetypeCard";
import RitualLaunchpadPanel from "../../components/swarm/RitualLaunchpadPanel";
import CodexInteractionLayer from "../../components/swarm/CodexInteractionLayer";

export default function MythOSOverviewPage() {
  return (
    <div className="container my-5">
      <h1>MythOS Overview</h1>
      <VisualArchetypeCard assistantId={1} />
      <RitualLaunchpadPanel />
      <CodexInteractionLayer />
    </div>
  );
}
