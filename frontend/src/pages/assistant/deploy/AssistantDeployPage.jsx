import { useParams } from "react-router-dom";
import DeploymentPlanner from "../../../components/assistants/DeploymentPlanner";

export default function AssistantDeployPage() {
  const { id } = useParams();
  return <DeploymentPlanner assistantId={id} />;
}
