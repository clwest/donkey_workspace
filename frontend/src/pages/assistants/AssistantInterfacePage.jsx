import React from "react";
import { useParams } from "react-router-dom";
import AssistantInterfaceRenderer from "../../components/assistant/AssistantInterfaceRenderer";

export default function AssistantInterfacePage() {
  const { id } = useParams();
  return <AssistantInterfaceRenderer assistantId={id} />;
}
