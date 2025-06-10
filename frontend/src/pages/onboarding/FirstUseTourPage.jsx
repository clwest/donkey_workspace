import { useEffect, useState } from "react";
import Tour from "@/components/onboarding/Tour";
import apiFetch from "@/utils/apiClient";
import { useNavigate } from "react-router-dom";
import useAuthGuard from "@/hooks/useAuthGuard";

export default function FirstUseTourPage() {
  useAuthGuard();
  const [steps, setSteps] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function init() {
      try {
        const assistants = await apiFetch("/assistants/");
        const slug = assistants[0]?.slug;
        if (!slug) return navigate("/assistant-dashboard");
        setSteps([
          {
            target: "#dashboard-page",
            content: "All your assistants live here",
            path: "/assistant-dashboard",
          },
          {
            target: "#trust-panel",
            content: "Review trust signals",
            path: `/assistants/${slug}/trust_profile/`,
          },
          {
            target: "#trail-page",
            content: "Timeline of major milestones",
            path: `/assistants/${slug}/trail/`,
          },
          {
            target: "#growth-panel",
            content: "Track growth progress",
            path: `/assistants/${slug}/growth/`,
          },
        ]);
      } catch {
        navigate("/assistant-dashboard");
      }
    }
    init();
  }, [navigate]);

  const handleFinish = async () => {
    try {
      const user = await apiFetch("/user/");
      if (user.authenticated) {
        await apiFetch(`/users/${user.id}/tours/complete/`, { method: "POST" });
      }
    } catch {}
    navigate("/assistant-dashboard");
  };

  if (!steps) return <div className="container my-5">Loading...</div>;
  return <Tour steps={steps} onFinish={handleFinish} />;
}
