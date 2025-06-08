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
      } catch (err) {
        if (err.message && err.message.includes("404")) {
          navigate("/assistants/primary/create");
        } else {
          console.error("Primary endpoint unreachable", err);
        }
      }
    }
    go();
  }, [navigate]);
  if (SHOW_INACTIVE_ROUTES) {
    return <ComingSoon title="Primary Assistant" />;
  }
  return null;
}
