import { useParams } from "react-router-dom";
import AssistantMythRebirthFramework from "../../../components/assistants/AssistantMythRebirthFramework";

export default function AssistantMythRebirthPage() {
  const { id } = useParams();
  return <AssistantMythRebirthFramework assistantId={id} />;
}
