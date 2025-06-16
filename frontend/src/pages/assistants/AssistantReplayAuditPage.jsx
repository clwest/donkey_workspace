import { useState } from "react";
import { useParams } from "react-router-dom";
import useAuthGuard from "../../hooks/useAuthGuard";
import useReplayLogs from "../../hooks/useReplayLogs";
import useDriftSnapshots from "../../hooks/useDriftSnapshots";
import ReplayLogTable from "../../components/assistant/ReplayLogTable";
import ReplayDriftModal from "../../components/assistant/ReplayDriftModal";

export default function AssistantReplayAuditPage() {
  useAuthGuard();
  const { slug } = useParams();
  const logs = useReplayLogs(slug);
  const [openId, setOpenId] = useState(null);
  const snapshots = useDriftSnapshots(openId);
  return (
    <div className="container my-4">
      <h2 className="mb-3">Symbolic Replays</h2>
      <ReplayLogTable logs={logs} slug={slug} onView={setOpenId} />
      {openId && (
        <ReplayDriftModal snapshots={snapshots} onClose={() => setOpenId(null)} />
      )}
    </div>
  );
}
