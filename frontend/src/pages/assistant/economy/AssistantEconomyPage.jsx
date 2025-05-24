import { useParams } from "react-router-dom";
import AssistantAlignmentToolset from "../../components/assistants/AssistantAlignmentToolset";

export default function AssistantEconomyPage() {
  const { id } = useParams();
  return <AssistantAlignmentToolset assistantId={id} />;
}
