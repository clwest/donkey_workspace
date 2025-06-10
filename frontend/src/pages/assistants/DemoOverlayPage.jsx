import { useParams } from "react-router-dom";
import useDemoSession from "@/hooks/useDemoSession";
import DemoOverlayPanel from "@/components/demo/DemoOverlayPanel";

export default function DemoOverlayPage() {
  const { slug } = useParams();
  const { demoSessionId } = useDemoSession();
  return (
    <div className="container my-5" id="demo-overlay-page">
      <h1 className="mb-3">Demo Overlay</h1>
      <DemoOverlayPanel slug={slug} sessionId={demoSessionId} />
    </div>
  );
}
