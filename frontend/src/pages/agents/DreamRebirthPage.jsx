import ReturnCycleViewer from "../../components/swarm/ReturnCycleViewer";
import ResurrectionTemplateEditor from "../../components/swarm/ResurrectionTemplateEditor";

export default function DreamRebirthPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-3">Dream Rebirth Console</h1>
      <ReturnCycleViewer />
      <ResurrectionTemplateEditor />
    </div>
  );
}
