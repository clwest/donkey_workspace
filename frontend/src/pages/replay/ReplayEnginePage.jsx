import PurposeLoopPlayer from "../../components/swarm/PurposeLoopPlayer";
import MemoryReplayPanel from "../../components/swarm/MemoryReplayPanel";

export default function ReplayEnginePage() {
  return (
    <div className="container my-5">
      <h1 className="mb-3">Belief Replay Engine</h1>
      <PurposeLoopPlayer />
      <MemoryReplayPanel />
    </div>
  );
}
