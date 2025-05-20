import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchCouncilSession } from "../../../api/council";
import LiveCouncilPanel from "../../../components/assistant/LiveCouncilPanel";

export default function CouncilDashboardPage() {
  const { id } = useParams();
  const [session, setSession] = useState(null);

  useEffect(() => {
    fetchCouncilSession(id)
      .then(setSession)
      .catch((e) => console.error("Failed to load session", e));
  }, [id]);

  if (!session) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-3">🧑‍💼 AI Council: {session.topic}</h2>
      <LiveCouncilPanel sessionId={id} />
    </div>
  );
}
