import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ComingSoon from "../../../components/common/ComingSoon";
import { SHOW_INACTIVE_ROUTES } from "../../../config/ui";

export default function PrimaryAssistantPage() {
  const navigate = useNavigate();
  useEffect(() => {
    if (!SHOW_INACTIVE_ROUTES) {
      navigate("/assistants/primary/dashboard");
    }
  }, [navigate]);
  if (SHOW_INACTIVE_ROUTES) {
    return <ComingSoon title="Primary Assistant" />;
  }
  return null;
}
