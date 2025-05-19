import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function PrimaryAssistantPage() {
  const navigate = useNavigate();
  useEffect(() => {
    navigate("/assistants/primary/dashboard");
  }, [navigate]);
  return null;
}
