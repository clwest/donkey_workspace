import { useParams } from "react-router-dom";
import AssistantToolChooser from "../../../components/assistants/AssistantToolChooser";

export default function AssistantToolsPage() {
  const { id } = useParams();
  return <AssistantToolChooser assistantId={id} />;
}
