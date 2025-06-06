import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ComingSoon from "../../../components/common/ComingSoon";
import { SHOW_INACTIVE_ROUTES } from "../../../config/ui";
import apiFetch from "../../../utils/apiClient";

export default function PrimaryAssistantPage() {
  const navigate = useNavigate();
  useEffect(() => {
    async function go() {
      if (SHOW_INACTIVE_ROUTES) return;
      try {
        const res = await apiFetch("/assistants/primary/");
        navigate(`/assistants/${res.slug}/dashboard`);
      } catch {
        navigate("/assistants/primary/create");
      }
    }
    go();
  }, [navigate]);
  if (SHOW_INACTIVE_ROUTES) {
    return <ComingSoon title="Primary Assistant" />;
  }
  return null;
}
