import { useState } from "react";
import { initiateReincarnation } from "../../api/agents";

export default function ReincarnationInterface({ assistantId }) {
  const [proposal, setProposal] = useState(null);

  const handleStart = async () => {
    try {
      const data = await initiateReincarnation(assistantId);
      setProposal(data);
    } catch (err) {
      console.error("Failed to initiate reincarnation", err);
    }
  };

  return (
    <div className="my-3">
      <button className="btn btn-primary" onClick={handleStart}>
        Begin Reincarnation
      </button>
      {proposal && (
        <pre className="mt-2 bg-light p-2 rounded">
          {JSON.stringify(proposal, null, 2)}
        </pre>
      )}
    </div>
  );
}
