import { useParams } from "react-router-dom";
import ComingSoon from "../../components/common/ComingSoon";

export default function BeliefCascadePage() {
  const { clauseId } = useParams();
  return <ComingSoon title={`Belief Cascade for ${clauseId}`} />;
}
