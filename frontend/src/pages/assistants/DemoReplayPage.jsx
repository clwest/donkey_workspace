import { useParams } from "react-router-dom";
import DemoReplayDebugger from "@/components/demo/DemoReplayDebugger";

export default function DemoReplayPage() {
  const { slug, sessionId } = useParams();
  return (
    <div className="container my-5" id="demo-replay-page">
      <h1 className="mb-3">Demo Replay</h1>
      <DemoReplayDebugger slug={slug} sessionId={sessionId} />
    </div>
  );
}
