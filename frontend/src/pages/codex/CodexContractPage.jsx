import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import LoadingSpinner from "../../components/LoadingSpinner";
import PromptContractCard from "../../components/codex/PromptContractCard";
import ClauseLineageViewer from "../../components/codex/ClauseLineageViewer";
import SymbolicObligationList from "../../components/codex/SymbolicObligationList";

export default function CodexContractPage() {
  const { promptId } = useParams();
  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!promptId) return;
    apiFetch(`/prompts/${promptId}/contract/`)
      .then(setContract)
      .catch((err) => {
        console.error("Failed to load contract", err);
        setContract(null);
      })
      .finally(() => setLoading(false));
  }, [promptId]);

  if (loading) return <LoadingSpinner />;
  if (!contract)
    return <div className="container my-5">❌ Contract not found.</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-3">Prompt Contract</h1>
      <PromptContractCard contract={contract} />
      <ClauseLineageViewer lineage={contract.lineage || []} />
      <SymbolicObligationList obligations={contract.obligations || []} />
    </div>
  );
}
