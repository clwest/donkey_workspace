import React from "react";
import { useParams } from "react-router-dom";
import AssistantInterfaceFramework from "../../components/assistant/AssistantInterfaceFramework";

export default function AssistantInterfacePage() {
  const { id } = useParams();
  return <AssistantInterfaceFramework assistantId={id} />;
}
