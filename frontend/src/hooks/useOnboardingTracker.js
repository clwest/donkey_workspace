import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useOnboardingTracker() {
  const [status, setStatus] = useState(null);

  const refreshStatus = async () => {
    if (!localStorage.getItem("access")) return;
    try {
      const res = await apiFetch("/onboarding/status/");
      setStatus(res);
      return res;
    } catch (err) {
      console.error("onboarding status error", err);
    }
  };

  const completeStep = async (step) => {
    if (!localStorage.getItem("access")) return;
    try {
      const res = await apiFetch("/onboarding/complete/", {
        method: "POST",
        body: { step },
      });
      setStatus(res);
      return res;
    } catch (err) {
      console.error("complete step error", err);
    }
  };

  useEffect(() => {
    if (localStorage.getItem("access")) {
      refreshStatus();
    }
  }, []);

  return {
    progress: status?.progress,
    nextStep: status?.next_step,
    percent: status?.percent,
    refreshStatus,
    completeStep,
  };
}
